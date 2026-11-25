"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Day-to-Night Mobility Transition & 24/7 Retail Activation Profiler
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
SVI_CSV = os.path.join(REPORTS_DIR, "store_viability_rankings.csv")
OUTPUT_PROFILES_CSV = os.path.join(REPORTS_DIR, "day_night_mobility_profiles.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "day_night_summary.json")

def analyze_day_night_activation():
    print("=" * 70)
    print("GeoPulse: Profiling Day-to-Night Mobility & 24/7 Retail Activation")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)

    # 1. Query footfall by sensor and hour of day
    print("1. Aggregating hourly footfall distributions from SQLite warehouse...")
    query = """
    SELECT 
        sensor_id,
        sensor_name,
        time as hour_of_day,
        AVG(hourly_counts) as avg_hourly_counts,
        SUM(hourly_counts) as total_hourly_volume
    FROM hourly_pedestrian_counts
    GROUP BY sensor_id, sensor_name, time
    """
    df_hourly = pd.read_sql_query(query, conn)
    conn.close()

    # Load SVI and Precinct metadata
    df_svi = pd.read_csv(SVI_CSV)[['sensor_id', 'precinct_name', 'store_viability_index']] if os.path.exists(SVI_CSV) else pd.DataFrame()

    results = []
    sensor_ids = df_hourly['sensor_id'].unique()

    for sid in sensor_ids:
        sensor_rows = df_hourly[df_hourly['sensor_id'] == sid]
        sensor_name = sensor_rows.iloc[0]['sensor_name']

        # Hourly mapping
        hour_map = dict(zip(sensor_rows['hour_of_day'], sensor_rows['avg_hourly_counts']))

        # Define Dayparts:
        # Daytime: 06:00 to 17:59 (hours 6 through 17)
        # Nighttime: 18:00 to 05:59 (hours 18 through 23, and 0 through 5)
        # Late Night Economy: 21:00 to 02:59 (hours 21, 22, 23, 0, 1, 2)
        # Morning Commute: 07:00 to 09:59 (hours 7, 8, 9)
        # Midday Lunch: 11:00 to 14:59 (hours 11, 12, 13, 14)
        # Evening Rush: 16:00 to 19:59 (hours 16, 17, 18, 19)

        day_hours = list(range(6, 18))
        night_hours = list(range(18, 24)) + list(range(0, 6))
        late_night_hours = [21, 22, 23, 0, 1, 2]

        day_vol = sum(hour_map.get(h, 0.0) for h in day_hours)
        night_vol = sum(hour_map.get(h, 0.0) for h in night_hours)
        late_night_vol = sum(hour_map.get(h, 0.0) for h in late_night_hours)
        total_24h_vol = day_vol + night_vol

        # Ratios and Shares
        day_share_pct = (day_vol / total_24h_vol * 100.0) if total_24h_vol > 0 else 50.0
        night_share_pct = (night_vol / total_24h_vol * 100.0) if total_24h_vol > 0 else 50.0
        late_night_share_pct = (late_night_vol / total_24h_vol * 100.0) if total_24h_vol > 0 else 10.0

        day_to_night_ratio = (day_vol / max(night_vol, 1.0))

        # Late-Night Vitality Index (LNVI): 0 to 100 normalized
        lnvi_score = min(max((late_night_share_pct / 25.0) * 100.0, 5.0), 100.0)

        # 24/7 Activation Classification
        if day_to_night_ratio <= 1.6 and total_24h_vol >= 5000:
            activation_type = "Vibrant 24/7 Mixed-Use Hub"
            recommended_hours = "24-Hour Operation / Extended Nighttime License"
        elif day_to_night_ratio <= 1.8 and late_night_share_pct >= 15.0:
            activation_type = "Nightlife & Evening Dining Corridor"
            recommended_hours = "Late Trade (11:00 AM - 02:00 AM)"
        elif day_to_night_ratio >= 2.8:
            activation_type = "Daytime Office / Commuter Focused"
            recommended_hours = "Standard Business Hours (06:30 AM - 06:30 PM)"
        else:
            activation_type = "Balanced Commercial Urban Spine"
            recommended_hours = "Extended Retail Hours (08:00 AM - 09:00 PM)"

        results.append({
            'sensor_id': sid,
            'sensor_name': sensor_name,
            'total_24h_daily_equivalent': round(total_24h_vol, 1),
            'day_volume_share_pct': round(day_share_pct, 1),
            'night_volume_share_pct': round(night_share_pct, 1),
            'late_night_share_pct': round(late_night_share_pct, 1),
            'day_to_night_ratio': round(day_to_night_ratio, 2),
            'late_night_vitality_index': round(lnvi_score, 1),
            'activation_archetype': activation_type,
            'recommended_trading_window': recommended_hours
        })

    df_res = pd.DataFrame(results)

    if not df_svi.empty:
        df_res = df_res.merge(df_svi, on='sensor_id', how='left')

    df_res = df_res.sort_values(by='total_24h_daily_equivalent', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_res.to_csv(OUTPUT_PROFILES_CSV, index=False)
    print(f"Day/Night activation profiles saved to: {OUTPUT_PROFILES_CSV}")

    # Summary JSON
    archetype_counts = df_res['activation_archetype'].value_counts().to_dict()
    summary = {
        "analysis_name": "GeoPulse Day-to-Night Mobility Transition & 24/7 Activation",
        "total_sensors_profiled": len(df_res),
        "mean_day_volume_share_pct": round(float(df_res['day_volume_share_pct'].mean()), 1),
        "mean_night_volume_share_pct": round(float(df_res['night_volume_share_pct'].mean()), 1),
        "mean_late_night_vitality_index": round(float(df_res['late_night_vitality_index'].mean()), 1),
        "activation_archetype_distribution": archetype_counts,
        "top_5_late_night_vitality_corridors": df_res.sort_values(by='late_night_vitality_index', ascending=False).head(5)[[
            'sensor_name', 'late_night_vitality_index', 'day_to_night_ratio', 'activation_archetype'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Day/Night summary saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- 24/7 ACTIVATION ARCHETYPE BREAKDOWN ---")
    for arch, count in archetype_counts.items():
        print(f"  • {arch}: {count} locations ({count/len(df_res)*100:.1f}%)")

    return df_res

if __name__ == '__main__':
    analyze_day_night_activation()
