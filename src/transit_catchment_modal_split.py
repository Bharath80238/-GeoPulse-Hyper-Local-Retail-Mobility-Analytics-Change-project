"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Transit Catchment Modal Split & Commuter Gravity Engine
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
OUTPUT_TRANSIT_CSV = os.path.join(REPORTS_DIR, "transit_catchment_modal_split.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "transit_modal_summary.json")

def model_transit_modal_split():
    print("=" * 70)
    print("GeoPulse: Modeling Transit Modal Split & Commuter Gateway Gravity")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        s.sensor_id,
        s.sensor_name,
        COALESCE(s.sensor_description, s.sensor_name) as sensor_desc,
        AVG(h.hourly_counts) as avg_hourly_footfall,
        AVG(CASE WHEN h.time IN (7, 8, 9, 17, 18) THEN h.hourly_counts ELSE NULL END) as peak_commute_footfall
    FROM sensor_locations s
    JOIN hourly_pedestrian_counts h ON s.sensor_id = h.sensor_id
    GROUP BY s.sensor_id, s.sensor_name, s.sensor_description
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Identify transit hub proximity (Train stations, tram super-stops)
    results = []
    for _, row in df.iterrows():
        name = row['sensor_desc'].lower()
        is_major_rail = any(t in name for t in ['flinders', 'spencer', 'southern cross', 'melbourne central'])
        is_tram_corridor = any(t in name for t in ['swanston', 'elizabeth', 'bourke', 'collins'])

        if is_major_rail:
            transit_role = "Major Rail Terminal / High-Volume Gateway"
            rail_share = 0.65
            tram_share = 0.20
            ped_share = 0.15
        elif is_tram_corridor:
            transit_role = "High-Frequency Tram Commercial Spine"
            rail_share = 0.25
            tram_share = 0.50
            ped_share = 0.25
        else:
            transit_role = "Pedestrian Laneway / Local Destination"
            rail_share = 0.15
            tram_share = 0.25
            ped_share = 0.60

        commute_intensity = (row['peak_commute_footfall'] / max(row['avg_hourly_footfall'], 1.0))

        results.append({
            'sensor_id': row['sensor_id'],
            'sensor_name': row['sensor_desc'],
            'transit_role': transit_role,
            'avg_hourly_footfall': round(row['avg_hourly_footfall'], 1),
            'peak_commute_footfall': round(row['peak_commute_footfall'], 1),
            'commute_intensity_ratio': round(commute_intensity, 2),
            'modal_share_heavy_rail_pct': round(rail_share * 100.0, 1),
            'modal_share_tram_light_rail_pct': round(tram_share * 100.0, 1),
            'modal_share_pure_pedestrian_pct': round(ped_share * 100.0, 1)
        })

    df_out = pd.DataFrame(results).sort_values(by='commute_intensity_ratio', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_out.to_csv(OUTPUT_TRANSIT_CSV, index=False)
    print(f"Transit modal split saved to: {OUTPUT_TRANSIT_CSV}")

    summary = {
        "analysis_name": "GeoPulse Transit Catchment Modal Split",
        "total_nodes_modeled": len(df_out),
        "role_breakdown": df_out['transit_role'].value_counts().to_dict(),
        "mean_commute_intensity_ratio": round(float(df_out['commute_intensity_ratio'].mean()), 2),
        "top_transit_gateways": df_out[df_out['transit_role'] == "Major Rail Terminal / High-Volume Gateway"].head(5)[[
            'sensor_name', 'commute_intensity_ratio', 'modal_share_heavy_rail_pct'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Transit summary saved to: {OUTPUT_SUMMARY_JSON}")

    return df_out

if __name__ == '__main__':
    model_transit_modal_split()
