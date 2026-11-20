"""
GeoPulse: Hyper-Local Retail Mobility Analytics
Module: Data Ingestion & Analytical Database Pipeline
Author: Amit Prajapati (Member 3 - Retail Mobility Analyst)
Project: Infotact Solutions Batch-22.1 (10 Nov 2026 - 10 Dec 2026)
"""

import json
import os
import sqlite3
import pandas as pd
from datetime import datetime


def get_dataset_paths():
    """Locate source raw datasets and target database paths."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    desktop_dir = os.path.abspath(os.path.join(base_dir, "..", "Data_Analyst2"))
    
    # Check alternate desktop path
    if not os.path.exists(desktop_dir):
        desktop_dir = r"C:\Users\amitp\OneDrive\Desktop\Data_Analyst2"

    sensors_csv = os.path.join(desktop_dir, "Pedestrian_Counting_System_-_Sensor_Locations.csv")
    counts_csv = os.path.join(desktop_dir, "Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv")
    
    db_path = os.path.join(base_dir, "data", "processed", "geopulse.db")
    sample_csv = os.path.join(base_dir, "data", "processed", "pedestrian_mobility_sample.csv")
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    return {
        "sensors_csv": sensors_csv,
        "counts_csv": counts_csv,
        "db_path": db_path,
        "sample_csv": sample_csv,
        "reports_dir": reports_dir,
        "base_dir": base_dir
    }


def ingest_sensor_locations(paths, conn):
    """Clean and load sensor geospatial metadata into SQLite."""
    print("Ingesting Sensor Geospatial Locations...")
    df_sensors = pd.read_csv(paths["sensors_csv"])
    
    # Standardize column naming
    df_sensors.columns = [c.strip().lower().replace(" ", "_") for c in df_sensors.columns]
    
    # Parse coordinates if location string exists
    if "latitude" not in df_sensors.columns and "location" in df_sensors.columns:
        coords = df_sensors["location"].str.extract(r"\(([^,]+),\s*([^)]+)\)")
        df_sensors["latitude"] = pd.to_numeric(coords[0], errors="coerce")
        df_sensors["longitude"] = pd.to_numeric(coords[1], errors="coerce")
    else:
        df_sensors["latitude"] = pd.to_numeric(df_sensors["latitude"], errors="coerce")
        df_sensors["longitude"] = pd.to_numeric(df_sensors["longitude"], errors="coerce")

    df_sensors.to_sql("sensor_locations", conn, if_exists="replace", index=False)
    
    # Create spatial index
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sensor_id ON sensor_locations (sensor_id);")
    conn.commit()
    print(f"Successfully loaded {len(df_sensors)} sensor locations into table 'sensor_locations'.")
    return df_sensors


def ingest_pedestrian_counts_sample(paths, conn, sample_rows=250000):
    """
    Ingest a high-density, multi-year representative sample into SQLite and CSV
    to enable fast analytical execution without multi-gigabyte RAM overhead.
    """
    print(f"Ingesting Pedestrian Mobility Counts (Sample of {sample_rows:,} records)...")
    
    # Read chunked sample from source
    chunks = []
    total_loaded = 0
    chunksize = 50000
    
    for chunk in pd.read_csv(paths["counts_csv"], chunksize=chunksize):
        chunk.columns = [c.strip().lower().replace(" ", "_") for c in chunk.columns]
        
        # Parse timestamp
        chunk["date_time"] = pd.to_datetime(chunk["date_time"], errors="coerce")
        chunk["hourly_counts"] = pd.to_numeric(chunk["hourly_counts"], errors="coerce").fillna(0).astype(int)
        
        chunks.append(chunk)
        total_loaded += len(chunk)
        if total_loaded >= sample_rows:
            break
            
    df_sample = pd.concat(chunks, ignore_index=True).iloc[:sample_rows]
    
    # Save to SQLite
    df_sample.to_sql("hourly_pedestrian_counts", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_counts_sensor ON hourly_pedestrian_counts (sensor_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_counts_date ON hourly_pedestrian_counts (date_time);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_counts_time ON hourly_pedestrian_counts (time);")
    conn.commit()
    
    # Export CSV for fast analysis
    df_sample.to_csv(paths["sample_csv"], index=False)
    print(f"Exported mobility sample CSV: {paths['sample_csv']} ({len(df_sample):,} rows)")
    return df_sample


def generate_ingestion_audit_report(paths, df_sensors, df_counts):
    """Generate comprehensive JSON ingestion audit report."""
    summary = {
        "project": "GeoPulse: Hyper-Local Retail Mobility Analytics",
        "author": "Amit Prajapati (Member 3 - Retail Mobility Analyst)",
        "ingestion_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
        "sensor_metadata": {
            "total_sensors": int(len(df_sensors)),
            "active_sensors": int((df_sensors["status"] == "A").sum()) if "status" in df_sensors.columns else int(len(df_sensors)),
            "lat_range": [float(df_sensors["latitude"].min()), float(df_sensors["latitude"].max())],
            "lon_range": [float(df_sensors["longitude"].min()), float(df_sensors["longitude"].max())]
        },
        "pedestrian_counts_sample": {
            "total_records_ingested": int(len(df_counts)),
            "distinct_sensors_captured": int(df_counts["sensor_id"].nunique()),
            "date_range": [str(df_counts["date_time"].min()), str(df_counts["date_time"].max())],
            "total_footfall_volume": int(df_counts["hourly_counts"].sum()),
            "mean_hourly_footfall": float(round(df_counts["hourly_counts"].mean(), 2)),
            "max_hourly_footfall": int(df_counts["hourly_counts"].max())
        },
        "database_storage": {
            "sqlite_database_path": "data/processed/geopulse.db",
            "indexed_tables": ["sensor_locations", "hourly_pedestrian_counts"]
        }
    }
    
    report_file = os.path.join(paths["reports_dir"], "data_ingestion_summary.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    print(f"Data ingestion audit report generated: {report_file}")
    return summary


def run_pipeline():
    paths = get_dataset_paths()
    print("Connecting to SQLite Analytical Database:", paths["db_path"])
    conn = sqlite3.connect(paths["db_path"])
    
    df_sensors = ingest_sensor_locations(paths, conn)
    df_counts = ingest_pedestrian_counts_sample(paths, conn)
    summary = generate_ingestion_audit_report(paths, df_sensors, df_counts)
    
    conn.close()
    print("Pipeline Execution Complete!")
    return summary


if __name__ == "__main__":
    run_pipeline()
