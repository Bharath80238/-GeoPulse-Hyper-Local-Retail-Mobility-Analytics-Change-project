"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Laneway Permeability & Secondary Street Attenuation Model
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
OUTPUT_LANEWAY_CSV = os.path.join(REPORTS_DIR, "laneway_permeability_metrics.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "laneway_summary.json")

def model_laneway_permeability():
    print("=" * 70)
    print("GeoPulse: Modeling Melbourne Laneway Permeability & Footfall Spillover")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        s.sensor_id,
        s.sensor_name,
        COALESCE(s.sensor_description, s.sensor_name) as full_name,
        s.latitude,
        s.longitude,
        AVG(h.hourly_counts) as avg_hourly_footfall
    FROM sensor_locations s
    JOIN hourly_pedestrian_counts h ON s.sensor_id = h.sensor_id
    GROUP BY s.sensor_id, s.sensor_name, s.sensor_description, s.latitude, s.longitude
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Identify laneway / arcade typology vs main boulevards
    def classify_street_type(name):
        n_low = name.lower()
        if any(term in n_low for term in ['la', 'lane', 'arcade', 'place', 'alley', 'little']):
            return "Secondary Laneway / Connector Arcade"
        elif any(term in n_low for term in ['mall', 'bridge', 'station', 'central']):
            return "Prime Pedestrian Concourse / Transit Hub"
        else:
            return "Primary Commercial Boulevard"

    df['street_typology'] = df['full_name'].apply(classify_street_type)

    # Laneway Permeability Index (LPI): relative footfall absorption
    bvd_mean = df[df['street_typology'] == "Primary Commercial Boulevard"]['avg_hourly_footfall'].mean()
    df['spillover_capture_ratio'] = (df['avg_hourly_footfall'] / max(bvd_mean, 1.0)).round(2)
    df['laneway_permeability_index'] = np.minimum(100.0, df['spillover_capture_ratio'] * 65.0).round(2)

    df_out = df.sort_values(by='laneway_permeability_index', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_out.to_csv(OUTPUT_LANEWAY_CSV, index=False)
    print(f"Laneway permeability metrics saved to: {OUTPUT_LANEWAY_CSV}")

    summary = {
        "analysis_name": "GeoPulse Melbourne Laneway Permeability Analytics",
        "typology_counts": df['street_typology'].value_counts().to_dict(),
        "mean_laneway_permeability_index": round(float(df['laneway_permeability_index'].mean()), 2),
        "top_permeable_laneways": df_out[df_out['street_typology'] == "Secondary Laneway / Connector Arcade"].head(5)[[
            'full_name', 'avg_hourly_footfall', 'laneway_permeability_index'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Laneway summary saved to: {OUTPUT_SUMMARY_JSON}")

    return df_out

if __name__ == '__main__':
    model_laneway_permeability()
