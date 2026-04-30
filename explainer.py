"""
explainer.py
------------
Explainable AI module for BioSense.

For each detected anomaly, generates:
  1. Confidence score (0-100%)
  2. Which sensor drove the anomaly
  3. What type of anomaly it is (spike, drift, dropout, correlated)
  4. Plain-English explanation of why the prediction was made
  5. Historical pattern count (how many times this happened before)
"""

import numpy as np
import pandas as pd


# Anomaly type detection thresholds
SPIKE_RATE_THRESHOLD = 2.0    # z-score change per reading = spike
DRIFT_MIN_DURATION = 5        # consecutive readings drifting = drift
DROPOUT_THRESHOLD = 0.05      # near-zero relative to mean = dropout


def anomaly_score_to_confidence(score: float) -> int:
    """
    Convert Isolation Forest anomaly score to a 0-100 confidence percentage.

    Isolation Forest scores:
      Positive (e.g. 0.1)  = normal (deep in the forest)
      Near zero (e.g. 0.0) = borderline
      Negative (e.g. -0.3) = anomaly (easy to isolate)

    We map the negative range to confidence:
      -0.5 or lower  → 95% confidence
      -0.1            → ~60% confidence
      0.0             → 40% confidence (borderline)
    """
    if score >= 0:
        return max(10, int(40 - score * 100))
    else:
        # More negative = higher confidence
        raw = min(abs(score) * 200, 95)
        return max(40, int(raw))


def detect_anomaly_type(values: np.ndarray, anomaly_indices: list, window: int = 10) -> str:
    """
    Determine what KIND of anomaly this is.

    Types:
      spike    — sudden jump up or down, then returns to normal
      drift    — slow creep in one direction over time
      dropout  — values drop to near zero (sensor failure)
      elevated — sustained high values without a sharp spike
    """
    if len(anomaly_indices) == 0:
        return "unknown"

    anom_values = values[anomaly_indices]
    normal_mean = np.mean(values)
    normal_std = np.std(values) + 1e-8

    # Check for dropout (values near zero relative to mean)
    if normal_mean != 0 and np.mean(anom_values) / abs(normal_mean) < DROPOUT_THRESHOLD:
        return "dropout"

    # Check for spike (short burst, value changes rapidly)
    if len(anomaly_indices) <= 3:
        return "spike"

    # Check for drift (values consistently moving in one direction)
    if len(anomaly_indices) >= DRIFT_MIN_DURATION:
        diffs = np.diff(anom_values)
        if np.all(diffs > 0) or np.all(diffs < 0):
            return "drift"
        # Mostly going in one direction
        if abs(np.sum(diffs > 0) - np.sum(diffs < 0)) / len(diffs) > 0.7:
            return "drift"

    return "elevated"


def find_primary_sensor(df: pd.DataFrame, sensor_cols: list, anomaly_idx: int) -> tuple:
    """
    Find which sensor contributed most to this anomaly.

    Returns (sensor_name, z_score, direction)
    """
    best_sensor = sensor_cols[0]
    best_z = 0
    direction = "high"

    for col in sensor_cols:
        mean = df[col].mean()
        std = df[col].std() + 1e-8
        val = df[col].iloc[anomaly_idx]
        z = (val - mean) / std

        if abs(z) > abs(best_z):
            best_z = z
            best_sensor = col
            direction = "above" if z > 0 else "below"

    return best_sensor, round(best_z, 1), direction


def count_historical_patterns(df: pd.DataFrame, anomaly_type: str, primary_sensor: str) -> int:
    """
    Count how many times this type of anomaly has occurred before.
    Uses the detected_anomaly column if available.
    """
    if "detected_anomaly" not in df.columns:
        return 0
    return int(df["detected_anomaly"].sum())


def generate_explanation(
    df: pd.DataFrame,
    sensor_cols: list,
    sensor_display: dict,
    anomaly_score: float,
    anomaly_indices: list,
    correlation_r: float = None,
    correlated_params: str = None,
) -> dict:
    """
    Generate a full explanation for a detected anomaly.

    Returns dict with:
      - confidence (int, 0-100)
      - anomaly_type (str)
      - primary_sensor (str)
      - z_score (float)
      - direction (str)
      - explanation (str, plain English)
      - technical_detail (str)
      - historical_count (int)
      - severity (str: critical / warning / info)
    """
    confidence = anomaly_score_to_confidence(anomaly_score)

    if not anomaly_indices:
        return {
            "confidence": confidence,
            "anomaly_type": "unknown",
            "primary_sensor": None,
            "explanation": "No clear anomaly pattern detected.",
            "technical_detail": f"Anomaly score: {anomaly_score:.3f}",
            "historical_count": 0,
            "severity": "info",
        }

    # Get the values for the most anomalous readings
    values_arr = df[sensor_cols[0]].values if sensor_cols else np.array([])
    anomaly_type = detect_anomaly_type(values_arr, anomaly_indices)

    # Find primary sensor
    primary_col, z_score, direction = find_primary_sensor(df, sensor_cols, anomaly_indices[-1])
    primary_label = sensor_display.get(primary_col, {}).get("label", primary_col.replace("_", " ").title())
    primary_unit = sensor_display.get(primary_col, {}).get("unit", "")

    # Current value
    current_val = round(df[primary_col].iloc[anomaly_indices[-1]], 2)
    normal_mean = round(df[primary_col].mean(), 2)

    # Historical count
    historical_count = count_historical_patterns(df, anomaly_type, primary_col)

    # Severity based on confidence and z-score
    if confidence >= 80 or abs(z_score) >= 5:
        severity = "critical"
    elif confidence >= 55 or abs(z_score) >= 3:
        severity = "warning"
    else:
        severity = "info"

    # Build plain-English explanation
    type_phrases = {
        "spike": f"{primary_label} jumped suddenly to {current_val} {primary_unit} — {abs(z_score):.1f}x further from normal than expected. This pattern suggests a brief event such as a door opening, a heating element glitch, or a momentary sensor fault.",
        "drift": f"{primary_label} has been gradually moving {direction} normal over {len(anomaly_indices)} consecutive readings, reaching {current_val} {primary_unit}. Slow drift usually indicates a developing equipment issue or environmental change — not a one-time event.",
        "dropout": f"{primary_label} dropped to near-zero ({current_val} {primary_unit}), which is consistent with a sensor disconnection, cable fault, or power interruption to the sensing element.",
        "elevated": f"{primary_label} has been sustained at {current_val} {primary_unit}, which is {direction} the expected normal range of {normal_mean} {primary_unit}. This may indicate an ongoing process or equipment issue.",
        "unknown": f"{primary_label} is showing unusual readings at {current_val} {primary_unit}.",
    }

    explanation = type_phrases.get(anomaly_type, type_phrases["unknown"])

    # Add correlation context if available
    if correlation_r and abs(correlation_r) > 0.6 and correlated_params:
        if correlation_r > 0:
            explanation += f" Additionally, {correlated_params} are moving together (correlation r={correlation_r:.2f}), suggesting a shared root cause rather than an isolated sensor issue."
        else:
            explanation += f" Note: {correlated_params} are moving in opposite directions (r={correlation_r:.2f}), which may indicate a compensating system response."

    # Technical detail line
    technical_detail = f"Anomaly score: {anomaly_score:.3f} · Z-score: {z_score:+.1f}σ · Type: {anomaly_type} · Readings flagged: {len(anomaly_indices)}"

    return {
        "confidence": confidence,
        "anomaly_type": anomaly_type,
        "primary_sensor": primary_label,
        "primary_unit": primary_unit,
        "current_value": current_val,
        "z_score": z_score,
        "direction": direction,
        "explanation": explanation,
        "technical_detail": technical_detail,
        "historical_count": historical_count,
        "severity": severity,
    }


def get_anomaly_explanations(df: pd.DataFrame, sensor_cols: list, sensor_display: dict) -> dict:
    """
    Generate explanations for each sensor column.

    Returns dict keyed by sensor column name, value is explanation dict.
    """
    explanations = {}

    for col in sensor_cols:
        # Find anomaly indices for this sensor
        if "detected_anomaly" in df.columns:
            anom_mask = df["detected_anomaly"] == 1
            anom_indices = list(df.index[anom_mask])
        else:
            anom_indices = []

        # Get worst anomaly score
        if "anomaly_score" in df.columns and len(anom_indices) > 0:
            worst_score = df.loc[anom_mask, "anomaly_score"].min()
        elif "anomaly_score" in df.columns:
            worst_score = df["anomaly_score"].min()
        else:
            worst_score = 0.0

        explanations[col] = generate_explanation(
            df=df,
            sensor_cols=sensor_cols,
            sensor_display=sensor_display,
            anomaly_score=worst_score,
            anomaly_indices=anom_indices,
        )

    return explanations


if __name__ == "__main__":
    # Quick test
    import sys
    sys.path.insert(0, '/home/claude/bioreactor-anomaly-detector')
    from data_generator import generate_bioreactor_data

    df = generate_bioreactor_data()
    sensor_cols = ["temperature_c", "ph", "dissolved_oxygen_pct"]
    sensor_display = {
        "temperature_c": {"label": "Temperature", "unit": "°C"},
        "ph": {"label": "pH", "unit": ""},
        "dissolved_oxygen_pct": {"label": "Dissolved O₂", "unit": "%"},
    }

    # Add mock anomaly detection
    df["detected_anomaly"] = 0
    df.loc[360:365, "detected_anomaly"] = 1
    df["anomaly_score"] = 0.1
    df.loc[360:365, "anomaly_score"] = -0.42

    explanations = get_anomaly_explanations(df, sensor_cols, sensor_display)
    for col, exp in explanations.items():
        print(f"\n{col}:")
        print(f"  Confidence: {exp['confidence']}%")
        print(f"  Type: {exp['anomaly_type']}")
        print(f"  Severity: {exp['severity']}")
        print(f"  Explanation: {exp['explanation'][:100]}...")
