"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Storefront Visibility Index & Visual Exposure Rating
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
OUTPUT_VISIBILITY_CSV = os.path.join(REPORTS_DIR, "storefront_visibility_ratings.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "visibility_summary.json")

def rate_storefront_visibility():
    print("=" * 70)
    print("GeoPulse: Modeling Storefront Visibility Index & Visual Exposure Ratings")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        s.sensor_id,
        s.sensor_name,
        COALESCE(s.sensor_description, s.sensor_name) as sensor_desc,
        s.direction_1,
        s.direction_2,
        AVG(h.hourly_counts) as avg_hourly_footfall
    FROM sensor_locations s
    JOIN hourly_pedestrian_counts h ON s.sensor_id = h.sensor_id
    GROUP BY s.sensor_id, s.sensor_name, s.sensor_description, s.direction_1, s.direction_2
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Model Visual Exposure Factors:
    # 1. Bi-directional flow visibility boost
    # 2. Corner / Intersection placement multiplier
    results = []
    for _, row in df.iterrows():
        desc = row['sensor_desc'].lower()
        is_corner = any(t in desc for t in ['-', '&', 'and', 'corner', 'cross'])
        has_dual_direction = (row['direction_1'] is not None and row['direction_2'] is not None)

        corner_boost = 1.35 if is_corner else 1.0
        dual_boost = 1.25 if has_dual_direction else 1.0

        # Exposure Factor
        exposure_factor = corner_boost * dual_boost
        effective_visual_impressions = row['avg_hourly_footfall'] * exposure_factor

        # Storefront Visibility Index (SVI-Vis, 0-100 scale)
        vis_index = min(100.0, (effective_visual_impressions / 1200.0) * 100.0)

        if vis_index >= 75.0:
            rating = "Grade A+ (Prime Corner / Panoramic View Corridor)"
        elif vis_index >= 50.0:
            rating = "Grade A (High Linear Boulevard Exposure)"
        elif vis_index >= 30.0:
            rating = "Grade B (Standard Mid-Block Storefront)"
        else:
            rating = "Grade C (Recessed / Low-Visibility Niche)"

        results.append({
            'sensor_id': row['sensor_id'],
            'sensor_name': row['sensor_desc'],
            'is_corner_intersection': is_corner,
            'is_dual_directional': has_dual_direction,
            'visual_exposure_multiplier': round(exposure_factor, 2),
            'avg_hourly_footfall': round(row['avg_hourly_footfall'], 1),
            'effective_visual_impressions': round(effective_visual_impressions, 1),
            'storefront_visibility_index': round(vis_index, 2),
            'visibility_grade': rating
        })

    df_out = pd.DataFrame(results).sort_values(by='storefront_visibility_index', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_out.to_csv(OUTPUT_VISIBILITY_CSV, index=False)
    print(f"Storefront visibility ratings saved to: {OUTPUT_VISIBILITY_CSV}")

    summary = {
        "analysis_name": "GeoPulse Storefront Visibility & Visual Exposure Model",
        "total_storefronts": len(df_out),
        "mean_visibility_index": round(float(df_out['storefront_visibility_index'].mean()), 2),
        "visibility_grade_distribution": df_out['visibility_grade'].value_counts().to_dict(),
        "top_exposed_storefronts": df_out.head(5)[[
            'sensor_name', 'visual_exposure_multiplier', 'storefront_visibility_index', 'visibility_grade'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Visibility summary saved to: {OUTPUT_SUMMARY_JSON}")

    return df_out

if __name__ == '__main__':
    rate_storefront_visibility()
