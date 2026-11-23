"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Dynamic Footfall Anomaly & Event Surge Detection Engine
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "geopulse.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_ANOMALIES_CSV = os.path.join(REPORTS_DIR, "footfall_anomalies_detected.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "anomaly_detection_summary.json")

def detect_footfall_anomalies():
    print("=" * 70)
    print("GeoPulse: Mining Temporal Footfall Anomalies & Event Surge Spikes")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}. Ingest data first.")

    conn = sqlite3.connect(DB_PATH)

    # Aggregate daily footfall per sensor
    print("1. Aggregating daily sensor telemetry from SQLite warehouse...")
    query = """
    SELECT 
        sensor_id,
        sensor_name,
        date(date_time) as obs_date,
        day as day_of_week,
        SUM(hourly_counts) as daily_volume,
        AVG(hourly_counts) as mean_hourly_volume,
        MAX(hourly_counts) as max_single_hour
    FROM hourly_pedestrian_counts
    GROUP BY sensor_id, sensor_name, obs_date, day
    HAVING COUNT(*) >= 12
    """
    df_daily = pd.read_sql_query(query, conn)
    conn.close()

    print(f"Loaded {len(df_daily):,} daily observation records across {df_daily['sensor_id'].nunique()} sensors.")

    # Compute sensor-level baseline distribution
    sensor_stats = df_daily.groupby('sensor_id')['daily_volume'].agg(['mean', 'std']).reset_index()
    sensor_stats.columns = ['sensor_id', 'sensor_mean_daily', 'sensor_std_daily']

    df_daily = df_daily.merge(sensor_stats, on='sensor_id', how='left')
    df_daily['sensor_std_daily'] = df_daily['sensor_std_daily'].replace(0, np.nan).fillna(1.0)

    # Standardized Z-Score
    df_daily['z_score'] = (df_daily['daily_volume'] - df_daily['sensor_mean_daily']) / df_daily['sensor_std_daily']

    # Classify anomalies
    def classify_anomaly(z):
        if z >= 2.5:
            return "Extreme Positive Surge (Event / Festival / Game Day)"
        elif z >= 1.8:
            return "Moderate Surge (Seasonal Trade)"
        elif z <= -2.2:
            return "Severe Deficit (Severe Weather / Transit Disruption)"
        elif z <= -1.5:
            return "Moderate Deficit (Trough / Holiday Lull)"
        else:
            return "Normal Baseline Activity"

    df_daily['anomaly_type'] = df_daily['z_score'].apply(classify_anomaly)

    anomalies_only = df_daily[df_daily['anomaly_type'] != "Normal Baseline Activity"].copy()
    anomalies_only = anomalies_only.sort_values(by='z_score', ascending=False)

    # Save anomalies dataset
    os.makedirs(REPORTS_DIR, exist_ok=True)
    export_cols = [
        'obs_date', 'day_of_week', 'sensor_id', 'sensor_name', 'daily_volume',
        'mean_hourly_volume', 'max_single_hour', 'z_score', 'anomaly_type'
    ]
    df_export = anomalies_only[export_cols]
    df_export.to_csv(OUTPUT_ANOMALIES_CSV, index=False)
    print(f"Detected anomalies saved to: {OUTPUT_ANOMALIES_CSV} ({len(df_export):,} anomaly records)")

    # Compute Sensor Volatility Index (Coefficient of Variation = std / mean * 100)
    volatility_df = df_daily.groupby(['sensor_id', 'sensor_name']).agg(
        total_days=('obs_date', 'count'),
        mean_daily=('daily_volume', 'mean'),
        std_daily=('daily_volume', 'std'),
        max_daily_surge=('daily_volume', 'max'),
        min_daily_trough=('daily_volume', 'min')
    ).reset_index()

    volatility_df['volatility_index_pct'] = (volatility_df['std_daily'] / volatility_df['mean_daily']) * 100.0
    volatility_df['volatility_index_pct'] = volatility_df['volatility_index_pct'].round(2)

    def classify_volatility(vi):
        if vi >= 60.0:
            return "High Volatility (Event / Transit Sensitive)"
        elif vi >= 40.0:
            return "Moderate Volatility (Balanced Commercial Flow)"
        else:
            return "Low Volatility (Highly Predictable Revenue Base)"

    volatility_df['predictability_tier'] = volatility_df['volatility_index_pct'].apply(classify_volatility)

    # Summary
    surge_count = len(df_daily[df_daily['anomaly_type'].str.contains("Surge")])
    deficit_count = len(df_daily[df_daily['anomaly_type'].str.contains("Deficit")])

    summary = {
        "analysis_name": "GeoPulse Dynamic Footfall Anomaly & Surge Mining",
        "total_sensor_days_evaluated": len(df_daily),
        "total_anomalies_flagged": len(anomalies_only),
        "positive_surges_count": surge_count,
        "negative_deficits_count": deficit_count,
        "mean_volatility_index_pct": round(float(volatility_df['volatility_index_pct'].mean()), 2),
        "top_5_extreme_surges": df_export.head(5)[[
            'obs_date', 'sensor_name', 'day_of_week', 'daily_volume', 'z_score', 'anomaly_type'
        ]].to_dict(orient='records'),
        "top_5_most_predictable_sensors": volatility_df.sort_values(by='volatility_index_pct').head(5)[[
            'sensor_name', 'volatility_index_pct', 'predictability_tier'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Anomaly detection summary JSON saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- TOP 3 EXTREME SURGE EVENTS MINED ---")
    for s in summary['top_5_extreme_surges'][:3]:
        print(f"• {s['obs_date']} ({s['day_of_week']}) at {s['sensor_name']}: {s['daily_volume']:,} pedestrians (Z = {s['z_score']:.2f})")

    return df_export

if __name__ == '__main__':
    detect_footfall_anomalies()
