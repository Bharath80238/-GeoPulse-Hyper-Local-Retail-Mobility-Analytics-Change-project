"""
GeoPulse: Hyper-Local Retail Mobility Analytics
Module: Temporal Mobility & Diurnal Footfall Dynamics Engine
Author: Amit Prajapati (Member 3 - Retail Mobility Analyst)
Project: Infotact Solutions Batch-22.1 (10 Nov 2026 - 10 Dec 2026)
"""

import json
import os
import sqlite3
import pandas as pd
import numpy as np


def analyze_temporal_mobility(db_path, reports_dir):
    """Analyze diurnal curves, retail peak hours, and weekend elasticity."""
    print("Executing Hyper-Local Temporal Mobility Analysis...")
    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT 
        c.sensor_id,
        s.sensor_name,
        c.time,
        c.day,
        c.month,
        c.hourly_counts
    FROM hourly_pedestrian_counts c
    JOIN sensor_locations s ON c.sensor_id = s.sensor_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # 1. 24-Hour Diurnal Hourly Curves
    diurnal = df.groupby(["time"]).agg(
        mean_footfall=("hourly_counts", "mean"),
        median_footfall=("hourly_counts", "median"),
        std_footfall=("hourly_counts", "std"),
        total_volume=("hourly_counts", "sum")
    ).reset_index()
    
    diurnal["mean_footfall"] = diurnal["mean_footfall"].round(1)
    diurnal["median_footfall"] = diurnal["median_footfall"].round(1)
    
    # Save hourly curves CSV
    diurnal_csv = os.path.join(reports_dir, "hourly_diurnal_curves.csv")
    diurnal.to_csv(diurnal_csv, index=False)
    print(f"Exported 24-hour diurnal curves: {diurnal_csv}")
    
    # 2. Peak Retail Dayparts
    def get_daypart(hour):
        if 7 <= hour <= 9: return "Morning Commute (07:00 - 09:59)"
        elif 11 <= hour <= 14: return "Lunch & Midday Retail (11:00 - 14:59)"
        elif 17 <= hour <= 19: return "Evening Shopping & Rush (17:00 - 19:59)"
        elif hour >= 21 or hour <= 4: return "Night-Time Economy (21:00 - 04:59)"
        else: return "Inter-Peak Hours"
        
    df["daypart"] = df["time"].apply(get_daypart)
    dayparts = df.groupby("daypart").agg(
        total_footfall=("hourly_counts", "sum"),
        avg_hourly=("hourly_counts", "mean")
    ).reset_index()
    
    total_all_footfall = df["hourly_counts"].sum()
    dayparts["volume_share_pct"] = ((dayparts["total_footfall"] / total_all_footfall) * 100).round(2)
    dayparts["avg_hourly"] = dayparts["avg_hourly"].round(1)
    
    # 3. Weekday vs Weekend Elasticity
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    df["is_weekend"] = (~df["day"].isin(weekdays)).astype(int)
    
    weekday_mean = df[df["is_weekend"] == 0]["hourly_counts"].mean()
    weekend_mean = df[df["is_weekend"] == 1]["hourly_counts"].mean()
    weekend_surge_ratio = round(weekend_mean / weekday_mean, 3) if weekday_mean > 0 else 1.0
    
    # Per-sensor weekend surge ratio
    sensor_elasticity = df.groupby(["sensor_id", "sensor_name", "is_weekend"])["hourly_counts"].mean().unstack().reset_index()
    sensor_elasticity.columns = ["sensor_id", "sensor_name", "weekday_mean", "weekend_mean"]
    sensor_elasticity["weekend_ratio"] = (sensor_elasticity["weekend_mean"] / sensor_elasticity["weekday_mean"]).round(2)
    
    def classify_behavior(ratio):
        if ratio >= 1.20: return "Weekend Destination / Leisure Hub"
        elif ratio <= 0.80: return "Weekday Commuter-Dominant Corridor"
        else: return "Balanced Commercial Zone"
        
    sensor_elasticity["retail_mobility_classification"] = sensor_elasticity["weekend_ratio"].apply(classify_behavior)
    
    elasticity_csv = os.path.join(reports_dir, "sensor_weekend_elasticity.csv")
    sensor_elasticity.to_csv(elasticity_csv, index=False)
    print(f"Exported sensor elasticity profile: {elasticity_csv}")
    
    # Compile summary JSON
    summary = {
        "analysis": "GeoPulse Temporal Mobility & Daypart Dynamics",
        "author": "Amit Prajapati (Member 3 - Retail Mobility Analyst)",
        "overall_footfall_volume": int(total_all_footfall),
        "peak_hourly_interval": int(diurnal.loc[diurnal["mean_footfall"].idxmax()]["time"]),
        "peak_hourly_mean_footfall": float(diurnal["mean_footfall"].max()),
        "weekday_mean_hourly": float(round(weekday_mean, 2)),
        "weekend_mean_hourly": float(round(weekend_mean, 2)),
        "weekend_surge_ratio": float(weekend_surge_ratio),
        "daypart_volume_shares": dayparts.to_dict(orient="records"),
        "retail_behavior_distribution": sensor_elasticity["retail_mobility_classification"].value_counts().to_dict()
    }
    
    summary_file = os.path.join(reports_dir, "temporal_patterns_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    print(f"Exported temporal patterns summary: {summary_file}")
    return summary


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_dir, "data", "processed", "geopulse.db")
    reports_dir = os.path.join(base_dir, "reports")
    analyze_temporal_mobility(db_path, reports_dir)
