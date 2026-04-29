"""
correlation.py
--------------
GAP 2: Multi-parameter correlation analysis.

This is the feature ATEK and PolySense DON'T have.

Their systems monitor each sensor independently:
  - Temperature > 38.5? Alert.
  - Humidity > 60%? Alert.
They never ask: "Are temperature AND humidity drifting together?"

WHY THAT MATTERS:
When two sensors drift in a correlated way, it usually means something
systemic is happening — not just a single sensor glitch. Examples:
  - Temperature rises AND humidity drops = HVAC failure
  - pH drops AND dissolved oxygen drops = cell culture crashing
  - Pressure drops AND temperature drops = seal leak

A single-sensor alert system sees two independent "warning" events.
Our correlation engine sees ONE root cause affecting both.
"""

import numpy as np
import pandas as pd


def analyze_correlations(df, sensor_cols, window=15):
    """
    Compute the correlation matrix between all sensor columns.

    Returns a dict with:
      - correlation_matrix: numpy array (n_sensors x n_sensors)
      - strong_pairs: list of (col_a, col_b, correlation) where |r| > 0.7
    """
    sensor_data = df[sensor_cols]
    corr_matrix = sensor_data.corr().values

    # Find strongly correlated pairs
    strong_pairs = []
    for i in range(len(sensor_cols)):
        for j in range(i + 1, len(sensor_cols)):
            r = corr_matrix[i][j]
            if abs(r) > 0.7:
                strong_pairs.append({
                    "sensor_a": sensor_cols[i],
                    "sensor_b": sensor_cols[j],
                    "correlation": round(r, 3),
                    "direction": "positive" if r > 0 else "negative",
                })

    return {
        "correlation_matrix": corr_matrix,
        "strong_pairs": strong_pairs,
    }


def detect_correlated_drifts(df, sensor_cols, window=15):
    """
    Detect time periods where multiple sensors drift together.

    HOW IT WORKS:
    1. Compute rolling z-scores for each sensor (how far from recent mean)
    2. For each time window, check if 2+ sensors are drifting simultaneously
    3. If they are, and their rolling correlation is strong, flag it

    A "correlated drift" means:
      - At least 2 sensors have z-scores > 1.5 in the same window
      - AND those sensors have a rolling correlation > 0.5 (or < -0.5)
      - AND this persists for at least 3 consecutive readings

    Returns a list of drift event dicts.
    """
    if len(df) < window * 2:
        return []

    drift_events = []

    # Rolling z-scores for each sensor
    z_scores = pd.DataFrame()
    for col in sensor_cols:
        rolling_mean = df[col].rolling(window=window, min_periods=5).mean()
        rolling_std = df[col].rolling(window=window, min_periods=5).std()
        z_scores[col] = (df[col] - rolling_mean) / (rolling_std + 1e-8)

    # For each pair of sensors, find windows where both are drifting
    for i in range(len(sensor_cols)):
        for j in range(i + 1, len(sensor_cols)):
            col_a = sensor_cols[i]
            col_b = sensor_cols[j]

            # Both drifting (z-score > 1.5) at the same time
            both_drifting = (
                (z_scores[col_a].abs() > 1.5) &
                (z_scores[col_b].abs() > 1.5)
            )

            # Rolling correlation between the pair
            rolling_corr = df[col_a].rolling(
                window=window, min_periods=5
            ).corr(df[col_b])

            # Strong correlation during drift
            correlated_drift = both_drifting & (rolling_corr.abs() > 0.5)

            # Find streaks of correlated drift (at least 3 consecutive)
            streak_count = 0
            streak_start = None

            for k in range(len(correlated_drift)):
                if correlated_drift.iloc[k]:
                    if streak_count == 0:
                        streak_start = k
                    streak_count += 1
                else:
                    if streak_count >= 3 and streak_start is not None:
                        # Record this event
                        start_time = df["timestamp"].iloc[streak_start]
                        end_time = df["timestamp"].iloc[k - 1]
                        avg_corr = rolling_corr.iloc[streak_start:k].mean()

                        # Determine what's happening
                        a_direction = "rising" if z_scores[col_a].iloc[streak_start:k].mean() > 0 else "dropping"
                        b_direction = "rising" if z_scores[col_b].iloc[streak_start:k].mean() > 0 else "dropping"

                        if avg_corr > 0:
                            pattern = f"Both {a_direction} together"
                        else:
                            pattern = f"{col_a} {a_direction} while {col_b} {b_direction}"

                        severity = "high" if streak_count >= 10 else "medium"

                        drift_events.append({
                            "parameters": f"{col_a} + {col_b}",
                            "start_time": start_time,
                            "end_time": end_time,
                            "time_range": f"{start_time} → {end_time}",
                            "duration_minutes": streak_count,
                            "avg_correlation": round(avg_corr, 3),
                            "pattern": pattern,
                            "severity": severity,
                            "message": f"{pattern} for {streak_count} min (r={avg_corr:.2f})",
                        })

                    streak_count = 0
                    streak_start = None

            # Handle streak at end of data
            if streak_count >= 3 and streak_start is not None:
                start_time = df["timestamp"].iloc[streak_start]
                end_time = df["timestamp"].iloc[len(df) - 1]
                avg_corr = rolling_corr.iloc[streak_start:].mean()
                a_direction = "rising" if z_scores[col_a].iloc[streak_start:].mean() > 0 else "dropping"
                b_direction = "rising" if z_scores[col_b].iloc[streak_start:].mean() > 0 else "dropping"

                if avg_corr > 0:
                    pattern = f"Both {a_direction} together"
                else:
                    pattern = f"{col_a} {a_direction} while {col_b} {b_direction}"

                severity = "high" if streak_count >= 10 else "medium"

                drift_events.append({
                    "parameters": f"{col_a} + {col_b}",
                    "start_time": start_time,
                    "end_time": end_time,
                    "time_range": f"{start_time} → {end_time}",
                    "duration_minutes": streak_count,
                    "avg_correlation": round(avg_corr, 3),
                    "pattern": pattern,
                    "severity": severity,
                    "message": f"{pattern} for {streak_count} min (r={avg_corr:.2f})",
                })

    # Sort by duration (longest/most serious first)
    drift_events.sort(key=lambda x: x["duration_minutes"], reverse=True)

    return drift_events


if __name__ == "__main__":
    from data_generator import generate_bioreactor_data

    df = generate_bioreactor_data()
    sensor_cols = ["temperature_c", "ph", "dissolved_oxygen_pct"]

    corr = analyze_correlations(df, sensor_cols)
    print("Correlation matrix:")
    print(corr["correlation_matrix"])
    print(f"\nStrong pairs: {corr['strong_pairs']}")

    drifts = detect_correlated_drifts(df, sensor_cols)
    print(f"\nCorrelated drift events: {len(drifts)}")
    for d in drifts[:5]:
        print(f"  {d['parameters']}: {d['message']}")
