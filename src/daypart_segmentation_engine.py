"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Daypart Baseline Segmentation & Diurnal Phase Profiler
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import json
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "geopulse.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_DAYPART_CSV = os.path.join(REPORTS_DIR, "daypart_baseline_segmentation.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "daypart_segmentation_summary.json")

def segment_dayparts():
    print("=" * 70)
    print("GeoPulse: Segmenting 24-Hour Diurnal Volume into 4 Standard Dayparts")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        time as hour_of_day,
        AVG(hourly_counts) as citywide_avg_hourly_footfall,
        SUM(hourly_counts) as citywide_total_volume
    FROM hourly_pedestrian_counts
    GROUP BY time
    ORDER BY time
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    total_volume = df['citywide_total_volume'].sum()
    df['volume_share_pct'] = ((df['citywide_total_volume'] / total_volume) * 100.0).round(2)

    def assign_daypart_name(h):
        if 6 <= h <= 10:
            return "Phase 1: Morning Commute & Breakfast (06:00 - 10:59)"
        elif 11 <= h <= 15:
            return "Phase 2: Midday Commercial & Lunch (11:00 - 15:59)"
        elif 16 <= h <= 19:
            return "Phase 3: Evening Rush & Happy Hour (16:00 - 19:59)"
        else:
            return "Phase 4: Late-Night & Overnight Economy (20:00 - 05:59)"

    df['daypart_phase'] = df['hour_of_day'].apply(assign_daypart_name)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df.to_csv(OUTPUT_DAYPART_CSV, index=False)
    print(f"Daypart segmentation saved to: {OUTPUT_DAYPART_CSV}")

    phase_agg = df.groupby('daypart_phase')['volume_share_pct'].sum().round(2).to_dict()
    summary = {
        "analysis_name": "GeoPulse Standard Diurnal Daypart Segmentation",
        "total_hourly_records": len(df),
        "phase_volume_shares_pct": phase_agg
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Daypart summary saved to: {OUTPUT_SUMMARY_JSON}")

    return df

if __name__ == '__main__':
    segment_dayparts()
