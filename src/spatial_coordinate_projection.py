"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Spatial Coordinate Projection & Planar Distance Modeling
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import json
import sqlite3
import math
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "geopulse.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_PROJECTION_CSV = os.path.join(REPORTS_DIR, "coordinate_projection_metrics.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "projection_summary.json")

def project_coordinates():
    print("=" * 70)
    print("GeoPulse: Projecting WGS84 Geodetic Coordinates to Planar Metric System")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT sensor_id, sensor_name, latitude, longitude FROM sensor_locations", conn)
    conn.close()

    # Local CBD origin: Flinders St / Swanston St intersection
    ORIGIN_LAT = -37.8180
    ORIGIN_LON = 144.9671

    # Planar approximation for hyper-local distances (meters per degree at latitude -37.8)
    METERS_PER_DEG_LAT = 110982.0
    METERS_PER_DEG_LON = 88020.0

    df['local_x_meters'] = ((df['longitude'] - ORIGIN_LON) * METERS_PER_DEG_LON).round(1)
    df['local_y_meters'] = ((df['latitude'] - ORIGIN_LAT) * METERS_PER_DEG_LAT).round(1)
    df['radial_distance_from_origin_m'] = (
        (df['local_x_meters']**2 + df['local_y_meters']**2)**0.5
    ).round(1)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df.to_csv(OUTPUT_PROJECTION_CSV, index=False)
    print(f"Projected coordinates saved to: {OUTPUT_PROJECTION_CSV}")

    summary = {
        "analysis_name": "GeoPulse Planar Metric Coordinate Transformation",
        "origin_reference": {"latitude": ORIGIN_LAT, "longitude": ORIGIN_LON, "label": "Flinders/Swanston Intersection"},
        "total_projected_nodes": len(df),
        "mean_radial_distance_m": round(float(df['radial_distance_from_origin_m'].mean()), 1),
        "max_radial_distance_m": round(float(df['radial_distance_from_origin_m'].max()), 1)
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Projection summary saved to: {OUTPUT_SUMMARY_JSON}")

    return df

if __name__ == '__main__':
    project_coordinates()
