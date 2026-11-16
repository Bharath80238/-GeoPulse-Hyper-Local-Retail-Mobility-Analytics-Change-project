"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Rush-Hour Arrival Velocity & Peak Flow Acceleration Engine
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
OUTPUT_VELOCITY_CSV = os.path.join(REPORTS_DIR, "rush_hour_arrival_velocity.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "rush_hour_summary.json")

def compute_rush_hour_velocity():
    print("=" * 70)
    print("GeoPulse: Modeling Morning & Evening Rush-Hour Arrival Acceleration")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)

    # Hourly mean footfall by sensor
    query = """
    SELECT 
        sensor_id,
        sensor_name,
        time as hour_of_day,
        AVG(hourly_counts) as avg_counts
    FROM hourly_pedestrian_counts
    GROUP BY sensor_id, sensor_name, time
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    results = []
    for sid, grp in df.groupby('sensor_id'):
        sname = grp.iloc[0]['sensor_name']
        hmap = dict(zip(grp['hour_of_day'], grp['avg_counts']))

        # Morning rush ramp: 06:00 to 08:00 delta
        morning_ramp = max(0.0, hmap.get(8, 0.0) - hmap.get(6, 0.0))
        morning_peak = max(hmap.get(7, 0.0), hmap.get(8, 0.0), hmap.get(9, 0.0))

        # Evening rush ramp: 15:00 to 17:00 delta
        evening_ramp = max(0.0, hmap.get(17, 0.0) - hmap.get(15, 0.0))
        evening_peak = max(hmap.get(16, 0.0), hmap.get(17, 0.0), hmap.get(18, 0.0))

        # Peak Hour Velocity Ratio
        off_peak_base = np.mean([hmap.get(h, 0.0) for h in [2, 3, 4, 10, 14, 21]])
        surge_multiplier = (max(morning_peak, evening_peak) / max(off_peak_base, 1.0))

        results.append({
            'sensor_id': sid,
            'sensor_name': sname,
            'morning_peak_volume': round(morning_peak, 1),
            'morning_ramp_acceleration': round(morning_ramp, 1),
            'evening_peak_volume': round(evening_peak, 1),
            'evening_ramp_acceleration': round(evening_ramp, 1),
            'off_peak_baseline': round(off_peak_base, 1),
            'rush_surge_multiplier': round(surge_multiplier, 2)
        })

    df_res = pd.DataFrame(results).sort_values(by='rush_surge_multiplier', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_res.to_csv(OUTPUT_VELOCITY_CSV, index=False)
    print(f"Rush hour velocity saved to: {OUTPUT_VELOCITY_CSV}")

    summary = {
        "analysis_name": "GeoPulse Rush-Hour Flow Acceleration Analytics",
        "total_sensors": len(df_res),
        "mean_surge_multiplier": round(float(df_res['rush_surge_multiplier'].mean()), 2),
        "top_surge_accelerators": df_res.head(5)[[
            'sensor_name', 'rush_surge_multiplier', 'morning_peak_volume', 'evening_peak_volume'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Rush hour summary saved to: {OUTPUT_SUMMARY_JSON}")

    return df_res

if __name__ == '__main__':
    compute_rush_hour_velocity()
