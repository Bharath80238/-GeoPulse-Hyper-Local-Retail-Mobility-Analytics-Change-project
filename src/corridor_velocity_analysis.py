"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Pedestrian Corridor Velocity & Flow Directionality Engine
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
OUTPUT_CORRIDOR_CSV = os.path.join(REPORTS_DIR, "corridor_pedestrian_velocity.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "corridor_flow_summary.json")

# Primary CBD Commercial Corridors
CORRIDOR_KEYWORDS = {
    "Bourke Street Spine": ["bourke"],
    "Swanston Street Promenade": ["swanston"],
    "Collins Street Luxury Strip": ["collins"],
    "Flinders Street Transit Strip": ["flinders"],
    "Elizabeth Street Corridor": ["elizabeth"],
    "Southbank Waterfront": ["southbank", "sandridge"],
    "Lonsdale / Chinatown": ["lonsdale", "chinatown", "little lonsdale"],
    "Spencer Street West Hub": ["spencer"]
}

def analyze_corridor_velocity():
    print("=" * 70)
    print("GeoPulse: Analyzing Street Corridor Velocity & Pedestrian Flow Dynamics")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)

    # 1. Fetch sensor location directional metadata and footfall
    query = """
    SELECT 
        s.sensor_id,
        s.sensor_name,
        COALESCE(s.sensor_description, s.sensor_name) as sensor_full_name,
        s.latitude,
        s.longitude,
        s.direction_1,
        s.direction_2,
        AVG(h.hourly_counts) as avg_hourly_footfall,
        MAX(h.hourly_counts) as peak_single_hour,
        SUM(CASE WHEN h.time IN (8, 9, 17, 18) THEN h.hourly_counts ELSE 0 END) * 1.0 / NULLIF(SUM(h.hourly_counts), 0) as rush_hour_ratio,
        SUM(CASE WHEN h.time IN (12, 13, 14, 19, 20) THEN h.hourly_counts ELSE 0 END) * 1.0 / NULLIF(SUM(h.hourly_counts), 0) as dwell_window_ratio
    FROM sensor_locations s
    JOIN hourly_pedestrian_counts h ON s.sensor_id = h.sensor_id
    GROUP BY s.sensor_id, s.sensor_name, s.sensor_description, s.latitude, s.longitude, s.direction_1, s.direction_2
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"Loaded {len(df)} sensor nodes with directional data.")

    # Assign Corridor
    def match_corridor(name):
        n_lower = name.lower()
        for corridor, keywords in CORRIDOR_KEYWORDS.items():
            if any(k in n_lower for k in keywords):
                return corridor
        return "Connecting Grid Laneway / Secondary Street"

    df['primary_corridor'] = df['sensor_full_name'].apply(match_corridor)

    # Fill NaNs for ratios
    df['rush_hour_ratio'] = df['rush_hour_ratio'].fillna(0.20)
    df['dwell_window_ratio'] = df['dwell_window_ratio'].fillna(0.25)

    # Compute Dwell Potential Index (DPI, 0-100 scale)
    # Browsing retail is characterized by higher midday/evening dwell vs commute rush
    # DPI = 100 * (dwell_window_ratio / (dwell_window_ratio + rush_hour_ratio))
    df['dwell_potential_index'] = (
        df['dwell_window_ratio'] / (df['dwell_window_ratio'] + df['rush_hour_ratio'])
    ) * 100.0
    df['dwell_potential_index'] = df['dwell_potential_index'].round(2)

    # Corridor Velocity Classification
    def classify_corridor_velocity(row):
        dpi = row['dwell_potential_index']
        vol = row['avg_hourly_footfall']

        if dpi >= 58.0 and vol >= 350.0:
            return "High-Dwell Retail Promenade (Experiential / Luxury / Dining)"
        elif dpi <= 46.0 and vol >= 400.0:
            return "High-Velocity Transit Conduit (QSR / Express Grab-and-Go)"
        elif vol >= 300.0:
            return "Balanced Commercial Arterial (General Retail)"
        else:
            return "Low-Velocity Neighborhood Stroll (Boutique / Niche Services)"

    df['corridor_velocity_classification'] = df.apply(classify_corridor_velocity, axis=1)

    # Format directions
    df['direction_profile'] = df.apply(
        lambda r: f"{r['direction_1'] or 'Bi-directional'} / {r['direction_2'] or 'Ambient'}", axis=1
    )

    export_cols = [
        'sensor_id', 'sensor_name', 'sensor_full_name', 'primary_corridor', 'direction_profile',
        'avg_hourly_footfall', 'peak_single_hour', 'dwell_potential_index',
        'corridor_velocity_classification'
    ]
    df_export = df[export_cols].sort_values(by='avg_hourly_footfall', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_export.to_csv(OUTPUT_CORRIDOR_CSV, index=False)
    print(f"Corridor velocity analytics saved to: {OUTPUT_CORRIDOR_CSV}")

    # Summary by major corridor
    corridor_summary = df.groupby('primary_corridor').agg(
        sensor_count=('sensor_id', 'count'),
        mean_hourly_footfall=('avg_hourly_footfall', 'mean'),
        mean_dwell_index=('dwell_potential_index', 'mean')
    ).round(2).reset_index().to_dict(orient='records')

    summary = {
        "analysis_name": "GeoPulse Pedestrian Corridor Velocity & Dwell Potential",
        "total_sensors_analyzed": len(df),
        "major_corridors_profiled": corridor_summary,
        "velocity_classification_distribution": df['corridor_velocity_classification'].value_counts().to_dict(),
        "top_dwell_promenades": df.sort_values(by='dwell_potential_index', ascending=False).head(5)[[
            'sensor_name', 'primary_corridor', 'dwell_potential_index', 'corridor_velocity_classification'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Corridor velocity summary saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- TOP CORRIDORS BY MEAN FOOTFALL ---")
    for c in sorted(corridor_summary, key=lambda x: x['mean_hourly_footfall'], reverse=True)[:4]:
        print(f"  • {c['primary_corridor']}: {c['mean_hourly_footfall']:.0f} pedestrians/hr (Dwell Index: {c['mean_dwell_index']})")

    return df_export

if __name__ == '__main__':
    analyze_corridor_velocity()
