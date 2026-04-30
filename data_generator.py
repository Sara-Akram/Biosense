"""
data_generator.py
-----------------
Generates fake lab sensor data with intentional anomalies injected.

Simulates a CO2 incubator / bioreactor environment with:
  - Temperature, pH, Dissolved Oxygen (bioreactor)
  - CO2, Humidity (ATEK-style incubator parameters)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_bioreactor_data(hours=24, readings_per_hour=60):
    """
    Create a DataFrame of lab sensor readings over `hours` hours.

    Normal ranges:
      - Temperature:        37.0 ± 0.3 °C
      - pH:                  7.0 ± 0.1
      - Dissolved oxygen:   40.0 ± 5 %
      - CO2:                 5.0 ± 0.3 %
      - Humidity:           95.0 ± 1.5 %RH

    Anomalies injected:
      1. Temperature spike (hour 6)
      2. pH drift (hour 14)
      3. DO dropout (hour 20)
      4. Temperature oscillation (hour 10)
      5. CO2 drop + humidity rise (correlated drift, hour 18)
    """

    total_points = hours * readings_per_hour
    np.random.seed(42)

    start = datetime.now() - timedelta(hours=hours)
    timestamps = [start + timedelta(minutes=i) for i in range(total_points)]

    # ── Normal baselines ─────────────────────────────────────
    temperature = 37.0 + np.random.normal(0, 0.15, total_points)
    ph = 7.0 + np.random.normal(0, 0.05, total_points)
    dissolved_oxygen = 40.0 + np.random.normal(0, 2.0, total_points)
    co2 = 5.0 + np.random.normal(0, 0.15, total_points)
    humidity = 95.0 + np.random.normal(0, 0.8, total_points)

    labels = np.zeros(total_points, dtype=int)

    # ── Anomaly 1: Temperature spike at hour 6 ───────────────
    spike_start = 6 * readings_per_hour
    spike_end = spike_start + 5
    temperature[spike_start:spike_end] = [39.8, 40.2, 39.5, 38.8, 38.2]
    labels[spike_start:spike_end] = 1

    # ── Anomaly 2: pH drift at hour 14 ───────────────────────
    drift_start = 14 * readings_per_hour
    drift_end = drift_start + 2 * readings_per_hour
    drift_length = drift_end - drift_start
    ph[drift_start:drift_end] += np.linspace(0, -0.5, drift_length)
    labels[drift_start:drift_end] = 1

    # ── Anomaly 3: DO dropout at hour 20 ─────────────────────
    dropout_start = 20 * readings_per_hour
    dropout_end = dropout_start + 8
    dissolved_oxygen[dropout_start:dropout_end] = np.random.uniform(0, 2, 8)
    labels[dropout_start:dropout_end] = 1

    # ── Anomaly 4: Temperature oscillation at hour 10 ────────
    osc_start = 10 * readings_per_hour
    osc_end = osc_start + 20
    temperature[osc_start:osc_end] = 37.0 + 1.2 * np.sin(np.linspace(0, 4 * np.pi, 20))
    labels[osc_start:osc_end] = 1

    # ── Anomaly 5: CO2 drop + humidity rise at hour 18 ───────
    # Correlated drift — door seal failure pattern
    corr_start = 18 * readings_per_hour
    corr_end = corr_start + 45
    co2[corr_start:corr_end] -= np.linspace(0, 1.8, 45)       # CO2 drops
    humidity[corr_start:corr_end] += np.linspace(0, 4.5, 45)  # humidity rises
    labels[corr_start:corr_end] = 1

    # ── Build DataFrame ───────────────────────────────────────
    df = pd.DataFrame({
        "timestamp": timestamps,
        "temperature_c": np.round(temperature, 2),
        "ph": np.round(ph, 3),
        "dissolved_oxygen_pct": np.round(np.clip(dissolved_oxygen, 0, 100), 1),
        "co2_pct": np.round(np.clip(co2, 0, 20), 2),
        "humidity_pct": np.round(np.clip(humidity, 0, 100), 1),
        "is_anomaly": labels,
    })

    return df


if __name__ == "__main__":
    df = generate_bioreactor_data()
    print(f"Generated {len(df)} readings over 24 hours")
    print(f"Anomalies injected: {df['is_anomaly'].sum()} points")
    print(df.head(5))
