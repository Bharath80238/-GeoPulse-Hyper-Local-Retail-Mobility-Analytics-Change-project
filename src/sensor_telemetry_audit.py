"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Sensor Hardware Telemetry Audit & Uptime Analyzer
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
OUTPUT_AUDIT_CSV = os.path.join(REPORTS_DIR, "sensor_hardware_audit_report.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "sensor_uptime_summary.json")

def audit_sensor_telemetry():
    print("=" * 70)
    print("GeoPulse: Auditing Sensor Telemetry Continuity & Uptime Metrics")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT 
        s.sensor_id,
        s.sensor_name,
        s.status,
        s.latitude,
        s.longitude,
        COUNT(h.id) as recorded_hourly_observations,
        SUM(h.hourly_counts) as total_pedestrian_volume,
        AVG(h.hourly_counts) as avg_hourly_footfall,
        MIN(h.date_time) as earliest_observation,
        MAX(h.date_time) as latest_observation,
        SUM(CASE WHEN h.hourly_counts = 0 THEN 1 ELSE 0 END) as zero_count_hours
    FROM sensor_locations s
    LEFT JOIN hourly_pedestrian_counts h ON s.sensor_id = h.sensor_id
    GROUP BY s.sensor_id, s.sensor_name, s.status, s.latitude, s.longitude
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Calculate telemetry integrity score (0-100 scale)
    max_obs = df['recorded_hourly_observations'].max()
    df['uptime_pct'] = ((df['recorded_hourly_observations'] / max(max_obs, 1)) * 100.0).round(2)
    df['zero_count_rate_pct'] = ((df['zero_count_hours'] / df['recorded_hourly_observations'].replace(0, np.nan)) * 100.0).fillna(0.0).round(2)

    def classify_telemetry_health(row):
        uptime = row['uptime_pct']
        zeros = row['zero_count_rate_pct']
        if uptime >= 85.0 and zeros <= 5.0:
            return "Optimal Health (High Fidelity Telemetry)"
        elif uptime >= 60.0:
            return "Acceptable Continuity (Moderate Gaps)"
        else:
            return "Intermittent / Sparsely Sampled Sensor"

    df['telemetry_health_tier'] = df.apply(classify_telemetry_health, axis=1)
    df = df.sort_values(by='recorded_hourly_observations', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df.to_csv(OUTPUT_AUDIT_CSV, index=False)
    print(f"Sensor audit report saved to: {OUTPUT_AUDIT_CSV}")

    summary = {
        "analysis_name": "GeoPulse Sensor Telemetry Integrity Audit",
        "total_sensors_audited": len(df),
        "mean_recorded_observations": round(float(df['recorded_hourly_observations'].mean()), 1),
        "mean_uptime_pct": round(float(df['uptime_pct'].mean()), 2),
        "telemetry_health_distribution": df['telemetry_health_tier'].value_counts().to_dict(),
        "top_reliable_sensors": df.head(5)[[
            'sensor_name', 'recorded_hourly_observations', 'uptime_pct', 'telemetry_health_tier'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Uptime summary saved to: {OUTPUT_SUMMARY_JSON}")

    return df

if __name__ == '__main__':
    audit_sensor_telemetry()
