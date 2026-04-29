"""
data_generator.py
-----------------
Generates fake bioreactor sensor data (temperature, pH, dissolved oxygen)
with intentional anomalies injected so the detector has something to find.

WHY THIS EXISTS:
Real bioreactor data is proprietary. For a demo, we simulate realistic
readings and inject known anomalies so we can prove the detector works.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_bioreactor_data(hours=24, readings_per_hour=60):
    """
    Create a DataFrame of bioreactor readings over `hours` hours.

    Normal ranges (what a real CHO cell culture bioreactor looks like):
      - Temperature: 37.0 ± 0.3 °C
      - pH: 7.0 ± 0.1
      - Dissolved oxygen (DO): 40 ± 5 %

    We inject 3 types of anomalies:
      1. SPIKE   — sudden jump (e.g. heating element glitch)
      2. DRIFT   — slow creep over time (e.g. pH probe fouling)
      3. DROPOUT — sensor returns 0 or NaN (e.g. cable disconnected)
    """

    total_points = hours * readings_per_hour
    np.random.seed(42)  # reproducible results for the demo

    # --- timestamps every minute ---
    start = datetime.now() - timedelta(hours=hours)
    timestamps = [start + timedelta(minutes=i) for i in range(total_points)]

    # --- normal baseline signals ---
    temperature = 37.0 + np.random.normal(0, 0.15, total_points)
    ph = 7.0 + np.random.normal(0, 0.05, total_points)
    dissolved_oxygen = 40.0 + np.random.normal(0, 2.0, total_points)

    # --- inject anomalies ---
    # We'll track which points are anomalies so we can check the detector later
    labels = np.zeros(total_points, dtype=int)  # 0 = normal, 1 = anomaly

    # ANOMALY 1: Temperature spike at hour 6 (points 360-365)
    spike_start = 6 * readings_per_hour
    spike_end = spike_start + 5
    temperature[spike_start:spike_end] = [39.8, 40.2, 39.5, 38.8, 38.2]
    labels[spike_start:spike_end] = 1

    # ANOMALY 2: pH drift starting at hour 14 (gradual decline over 2 hours)
    drift_start = 14 * readings_per_hour
    drift_end = drift_start + 2 * readings_per_hour
    drift_length = drift_end - drift_start
    ph_drift = np.linspace(0, -0.5, drift_length)  # drops from 7.0 to ~6.5
    ph[drift_start:drift_end] += ph_drift
    labels[drift_start:drift_end] = 1

    # ANOMALY 3: DO sensor dropout at hour 20 (readings go to near-zero)
    dropout_start = 20 * readings_per_hour
    dropout_end = dropout_start + 8
    dissolved_oxygen[dropout_start:dropout_end] = np.random.uniform(0, 2, 8)
    labels[dropout_start:dropout_end] = 1

    # ANOMALY 4: Small temperature oscillation at hour 10 (subtle)
    osc_start = 10 * readings_per_hour
    osc_end = osc_start + 20
    osc_pattern = 37.0 + 1.2 * np.sin(np.linspace(0, 4 * np.pi, 20))
    temperature[osc_start:osc_end] = osc_pattern
    labels[osc_start:osc_end] = 1

    # --- build DataFrame ---
    df = pd.DataFrame({
        "timestamp": timestamps,
        "temperature_c": np.round(temperature, 2),
        "ph": np.round(ph, 3),
        "dissolved_oxygen_pct": np.round(dissolved_oxygen, 1),
        "is_anomaly": labels,
    })

    return df


if __name__ == "__main__":
    # Quick test: generate and peek at the data
    df = generate_bioreactor_data()
    print(f"Generated {len(df)} readings over 24 hours")
    print(f"Anomalies injected: {df['is_anomaly'].sum()} points")
    print(df.head(10))
    print("\n--- Sample anomaly (temperature spike) ---")
    print(df.iloc[358:368])
