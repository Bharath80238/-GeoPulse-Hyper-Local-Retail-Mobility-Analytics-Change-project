"""
GeoPulse: Hyper-Local Retail Mobility Analytics
Module: Geospatial Sensor Profiling & Retail Precinct Clustering
Author: Amit Prajapati (Member 3 - Retail Mobility Analyst)
Project: Infotact Solutions Batch-22.1 (10 Nov 2026 - 10 Dec 2026)
"""

import json
import math
import os
import sqlite3
import pandas as pd
import numpy as np


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two coordinates on Earth."""
    r = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def assign_retail_precinct(lat, lon, name):
    """
    Classify sensor into high-impact retail mobility precincts based on
    Melbourne CBD geographical benchmarks and commercial retail zoning.
    """
    name_lower = str(name).lower()
    
    # Keyword & Boundary Rules
    if any(k in name_lower for k in ["bourke", "elizabeth st (north)", "midblock", "gpo"]):
        return "Central Retail Core (Bourke St Mall)"
    elif any(k in name_lower for k in ["flinders", "swanston", "federation", "princes"]):
        return "Flinders Transit Hub (Commuter Spine)"
    elif any(k in name_lower for k in ["southbank", "sandridge", "yarra", "promenade"]):
        return "Southbank Promenade & Waterfront"
    elif any(k in name_lower for k in ["docklands", "harbour", "waterfront"]):
        return "Docklands Harbourside Precinct"
    elif any(k in name_lower for k in ["chinatown", "little bourke", "russell", "exhibition"]):
        return "Chinatown & East End Dining"
    elif any(k in name_lower for k in ["lygon", "grattan", "university", "pelham"]):
        return "Northern University Corridor"
    else:
        # Spatial coordinate bounding assignment
        if lat < -37.820:
            return "Southbank Promenade & Waterfront"
        elif lon < 144.950:
            return "Docklands Harbourside Precinct"
        elif lat > -37.805:
            return "Northern University Corridor"
        elif lon > 144.968:
            return "Chinatown & East End Dining"
        elif -37.817 <= lat <= -37.810 and 144.960 <= lon <= 144.968:
            return "Central Retail Core (Bourke St Mall)"
        else:
            return "Flinders Transit Hub (Commuter Spine)"


def profile_sensor_geospatial(db_path, reports_dir):
    """Profile all sensors, assign retail precincts, and calculate spatial metrics."""
    print("Profiling Sensor Geospatial Networks...")
    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT 
        s.sensor_id,
        s.sensor_name,
        s.latitude,
        s.longitude,
        s.status,
        COUNT(c.hourly_counts) as total_observations,
        SUM(c.hourly_counts) as total_footfall,
        AVG(c.hourly_counts) as avg_hourly_footfall,
        MAX(c.hourly_counts) as peak_hourly_footfall
    FROM sensor_locations s
    LEFT JOIN hourly_pedestrian_counts c ON s.sensor_id = c.sensor_id
    WHERE s.latitude IS NOT NULL AND s.longitude IS NOT NULL
    GROUP BY s.sensor_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Melbourne CBD Anchor Point (Flinders St / Federation Square)
    cbd_lat, cbd_lon = -37.8179789, 144.9670984
    
    df["distance_to_cbd_center_m"] = df.apply(
        lambda r: round(haversine_distance(r["latitude"], r["longitude"], cbd_lat, cbd_lon), 1),
        axis=1
    )
    
    df["retail_precinct"] = df.apply(
        lambda r: assign_retail_precinct(r["latitude"], r["longitude"], r["sensor_name"]),
        axis=1
    )
    
    # Footfall density tier
    df["avg_hourly_footfall"] = df["avg_hourly_footfall"].fillna(0).round(1)
    df["total_footfall"] = df["total_footfall"].fillna(0).astype(int)
    
    q75 = df["avg_hourly_footfall"].quantile(0.75)
    q25 = df["avg_hourly_footfall"].quantile(0.25)
    
    def get_density_tier(val):
        if val >= q75: return "Tier 1: High Footfall Density (Prime Retail)"
        elif val >= q25: return "Tier 2: Moderate Footfall Density (Secondary Retail)"
        else: return "Tier 3: Low Footfall Density (Transit/Feeder)"
        
    df["density_tier"] = df["avg_hourly_footfall"].apply(get_density_tier)
    
    # Export spatial profile CSV
    out_csv = os.path.join(reports_dir, "sensor_spatial_profile.csv")
    df.to_csv(out_csv, index=False)
    print(f"Exported sensor spatial profile: {out_csv} ({len(df)} sensors)")
    
    # Precinct summary
    precinct_summary = df.groupby("retail_precinct").agg(
        sensor_count=("sensor_id", "count"),
        total_precinct_footfall=("total_footfall", "sum"),
        mean_hourly_footfall=("avg_hourly_footfall", "mean"),
        max_peak_footfall=("peak_hourly_footfall", "max"),
        mean_dist_to_cbd_m=("distance_to_cbd_center_m", "mean")
    ).reset_index()
    
    precinct_summary["mean_hourly_footfall"] = precinct_summary["mean_hourly_footfall"].round(1)
    precinct_summary["mean_dist_to_cbd_m"] = precinct_summary["mean_dist_to_cbd_m"].round(1)
    
    summary_dict = {
        "analysis_name": "GeoPulse Retail Precinct Spatial Profile",
        "author": "Amit Prajapati (Member 3 - Retail Mobility Analyst)",
        "total_sensors_mapped": int(len(df)),
        "active_precincts": precinct_summary.to_dict(orient="records")
    }
    
    out_json = os.path.join(reports_dir, "retail_precinct_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary_dict, f, indent=2)
        
    print(f"Exported retail precinct summary: {out_json}")
    return df, summary_dict


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_dir, "data", "processed", "geopulse.db")
    reports_dir = os.path.join(base_dir, "reports")
    profile_sensor_geospatial(db_path, reports_dir)
