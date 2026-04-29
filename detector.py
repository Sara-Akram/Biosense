"""
detector.py
-----------
Anomaly detection engine that combines two approaches:

1. STATISTICAL RULES (simple threshold + rate-of-change checks)
   - Catches obvious violations like "temperature > 38.5°C"
   - Easy to explain to regulators

2. ML MODEL (Isolation Forest from scikit-learn)
   - Catches subtle patterns humans might miss
   - Learns what "normal" looks like from the data itself

WHY BOTH?
Pharma companies need explainability. A pure ML model that says "anomaly"
without reason won't pass GxP validation. So we layer:
  - Rules catch the obvious stuff with clear explanations
  - ML catches the weird stuff the rules miss
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime


# --- Thresholds (based on typical CHO cell culture specs) ---
THRESHOLDS = {
    "temperature_c": {"min": 36.0, "max": 38.5, "rate_limit": 0.5},
    "ph": {"min": 6.80, "max": 7.20, "rate_limit": 0.05},
    "dissolved_oxygen_pct": {"min": 20.0, "max": 60.0, "rate_limit": 5.0},
}


def run_rule_based_detection(df):
    """
    Check each reading against static thresholds and rate-of-change limits.

    Returns a list of alert dicts with:
      - timestamp, parameter, alert_type, value, threshold, severity, message
    """
    alerts = []

    for param, limits in THRESHOLDS.items():
        values = df[param].values

        for i in range(len(df)):
            val = values[i]
            ts = df["timestamp"].iloc[i]

            # --- threshold violation ---
            if val > limits["max"]:
                alerts.append({
                    "timestamp": ts,
                    "parameter": param,
                    "alert_type": "threshold_high",
                    "value": round(val, 3),
                    "threshold": limits["max"],
                    "severity": "critical",
                    "message": f"{param} = {val:.2f} exceeds max {limits['max']}",
                })
            elif val < limits["min"]:
                alerts.append({
                    "timestamp": ts,
                    "parameter": param,
                    "alert_type": "threshold_low",
                    "value": round(val, 3),
                    "threshold": limits["min"],
                    "severity": "critical",
                    "message": f"{param} = {val:.2f} below min {limits['min']}",
                })

            # --- rate of change (compare to previous reading) ---
            if i > 0:
                rate = abs(val - values[i - 1])
                if rate > limits["rate_limit"]:
                    alerts.append({
                        "timestamp": ts,
                        "parameter": param,
                        "alert_type": "rate_change",
                        "value": round(val, 3),
                        "threshold": limits["rate_limit"],
                        "severity": "warning",
                        "message": f"{param} changed by {rate:.3f}/min (limit: {limits['rate_limit']})",
                    })

    return alerts


def run_ml_detection(df, contamination=0.02):
    """
    Use Isolation Forest to find anomalies the rules might miss.

    HOW ISOLATION FOREST WORKS (simple version):
    - It builds random decision trees that try to isolate each data point
    - Normal points are hard to isolate (deep in the tree)
    - Anomalies are easy to isolate (shallow in the tree)
    - Points that are consistently isolated quickly = anomalies

    The `contamination` parameter tells the model roughly what % of data
    is expected to be anomalous. We set it low (2%) to avoid false alarms.
    """
    features = df[["temperature_c", "ph", "dissolved_oxygen_pct"]].values

    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,  # number of trees
    )

    # fit and predict: -1 = anomaly, 1 = normal
    predictions = model.fit_predict(features)

    # anomaly scores (lower = more anomalous)
    scores = model.decision_function(features)

    return predictions, scores, model


def detect_anomalies(df):
    """
    Run both detection methods and merge results.

    Returns:
      - df with added columns: ml_anomaly, anomaly_score, detected_anomaly
      - alerts: list of rule-based alert dicts
      - model: the trained IsolationForest (for later inspection)
    """
    # --- Rule-based ---
    alerts = run_rule_based_detection(df)

    # --- ML-based ---
    predictions, scores, model = run_ml_detection(df)

    # Add ML results to DataFrame
    df = df.copy()
    df["ml_anomaly"] = (predictions == -1).astype(int)
    df["anomaly_score"] = np.round(scores, 4)

    # Combined: flagged by EITHER method
    # Rule-based flags come from alerts; mark those timestamps
    rule_timestamps = set()
    for alert in alerts:
        rule_timestamps.add(alert["timestamp"])

    df["rule_anomaly"] = df["timestamp"].isin(rule_timestamps).astype(int)
    df["detected_anomaly"] = ((df["ml_anomaly"] == 1) | (df["rule_anomaly"] == 1)).astype(int)

    return df, alerts, model


def build_audit_log(alerts, df):
    """
    Create a GxP-style audit trail from detection results.

    Each entry is timestamped and immutable — this is what regulators
    want to see: proof that the system caught the problem and logged it.
    """
    log_entries = []

    # Deduplicate alerts by timestamp+parameter (keep highest severity)
    seen = set()
    severity_rank = {"critical": 2, "warning": 1}

    sorted_alerts = sorted(alerts, key=lambda a: (a["timestamp"], -severity_rank.get(a["severity"], 0)))

    for alert in sorted_alerts:
        key = (alert["timestamp"], alert["parameter"])
        if key in seen:
            continue
        seen.add(key)

        log_entries.append({
            "log_id": f"EVT-{len(log_entries)+1:04d}",
            "timestamp": alert["timestamp"],
            "parameter": alert["parameter"],
            "alert_type": alert["alert_type"],
            "value": alert["value"],
            "threshold": alert["threshold"],
            "severity": alert["severity"],
            "message": alert["message"],
            "detection_method": "rule_based",
            "logged_at": datetime.now(),
        })

    # Add ML-only detections (not caught by rules)
    ml_only = df[(df["ml_anomaly"] == 1) & (df["rule_anomaly"] == 0)]
    for _, row in ml_only.iterrows():
        log_entries.append({
            "log_id": f"EVT-{len(log_entries)+1:04d}",
            "timestamp": row["timestamp"],
            "parameter": "multi_param",
            "alert_type": "ml_anomaly",
            "value": round(row["anomaly_score"], 4),
            "threshold": "model_threshold",
            "severity": "warning",
            "message": f"ML detected anomaly (score: {row['anomaly_score']:.4f})",
            "detection_method": "isolation_forest",
            "logged_at": datetime.now(),
        })

    return pd.DataFrame(log_entries)


if __name__ == "__main__":
    from data_generator import generate_bioreactor_data

    df = generate_bioreactor_data()
    df, alerts, model = detect_anomalies(df)

    print(f"Rule-based alerts: {len(alerts)}")
    print(f"ML anomalies: {df['ml_anomaly'].sum()}")
    print(f"Combined detections: {df['detected_anomaly'].sum()}")
    print(f"Actual anomalies in data: {df['is_anomaly'].sum()}")

    audit = build_audit_log(alerts, df)
    print(f"\nAudit log entries: {len(audit)}")
    print(audit.head(10))
