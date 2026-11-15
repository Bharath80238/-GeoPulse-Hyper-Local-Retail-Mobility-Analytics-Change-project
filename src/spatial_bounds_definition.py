"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Melbourne CBD Spatial Bounding Box & Coordinate Reference Frame
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
OUTPUT_GEOJSON = os.path.join(REPORTS_DIR, "melbourne_cbd_boundary_geometry.json")

def define_spatial_bounds():
    print("=" * 70)
    print("GeoPulse: Defining Spatial Bounding Box & Coordinate Reference Frame")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)
    df_sensors = pd.read_sql_query("SELECT sensor_id, sensor_name, latitude, longitude FROM sensor_locations", conn)
    conn.close()

    min_lat, max_lat = df_sensors['latitude'].min(), df_sensors['latitude'].max()
    min_lon, max_lon = df_sensors['longitude'].min(), df_sensors['longitude'].max()
    centroid_lat, centroid_lon = df_sensors['latitude'].mean(), df_sensors['longitude'].mean()

    boundary_data = {
        "coordinate_reference_system": "EPSG:4326 (WGS84)",
        "study_area": "Melbourne Central Business District (CBD) & Retail Environs",
        "total_georeferenced_sensors": len(df_sensors),
        "bounding_box": {
            "min_latitude": round(float(min_lat), 6),
            "max_latitude": round(float(max_lat), 6),
            "min_longitude": round(float(min_lon), 6),
            "max_longitude": round(float(max_lon), 6),
            "span_latitude_km": round((max_lat - min_lat) * 111.0, 3),
            "span_longitude_km": round((max_lon - min_lon) * 88.0, 3)
        },
        "retail_gravity_centroid": {
            "latitude": round(float(centroid_lat), 6),
            "longitude": round(float(centroid_lon), 6),
            "description": "Melbourne Town Hall / Bourke St Mall Intersection"
        },
        "quadrant_distribution": {
            "north_west": len(df_sensors[(df_sensors['latitude'] >= centroid_lat) & (df_sensors['longitude'] <= centroid_lon)]),
            "north_east": len(df_sensors[(df_sensors['latitude'] >= centroid_lat) & (df_sensors['longitude'] > centroid_lon)]),
            "south_west": len(df_sensors[(df_sensors['latitude'] < centroid_lat) & (df_sensors['longitude'] <= centroid_lon)]),
            "south_east": len(df_sensors[(df_sensors['latitude'] < centroid_lat) & (df_sensors['longitude'] > centroid_lon)])
        }
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(OUTPUT_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(boundary_data, f, indent=4)

    print(f"Spatial boundary metadata saved to: {OUTPUT_GEOJSON}")
    return boundary_data

if __name__ == '__main__':
    define_spatial_bounds()
