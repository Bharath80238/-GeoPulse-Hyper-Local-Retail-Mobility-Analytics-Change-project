"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Pedestrian Catchment Isochrone & Spatial Gravity Model
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import json
import math
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SVI_CSV = os.path.join(REPORTS_DIR, "store_viability_rankings.csv")
OUTPUT_CATCHMENT_CSV = os.path.join(REPORTS_DIR, "pedestrian_catchment_radii.csv")
OUTPUT_GRAVITY_JSON = os.path.join(REPORTS_DIR, "catchment_gravity_metrics.json")

def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def compute_pedestrian_catchments():
    print("=" * 70)
    print("GeoPulse: Modeling Pedestrian Catchment Isochrones & Spatial Gravity")
    print("=" * 70)

    if not os.path.exists(SVI_CSV):
        raise FileNotFoundError(f"Missing {SVI_CSV}. Run store_viability_index.py first.")

    df = pd.read_csv(SVI_CSV)
    print(f"Loaded {len(df)} sensors from Store Viability rankings.")

    # Parameters for Urban Pedestrian Isochrones:
    # Typical CBD walking speed: 4.5 km/h (~75 m/min)
    # Primary buffer: 300m (~4 min walk)
    # Secondary buffer: 600m (~8 min walk)
    # Tertiary buffer: 1000m (~13 min walk)
    R_PRIMARY = 300.0
    R_SECONDARY = 600.0
    R_TERTIARY = 1000.0
    BETA_DECAY = 1.5  # Urban pedestrian decay exponent

    results = []
    gravity_records = {}

    for idx, row in df.iterrows():
        sensor_id = row['sensor_id']
        sensor_name = row['sensor_name']
        precinct = row['precinct_name']
        lat_i, lon_i = row['latitude'], row['longitude']
        vol_i = row['avg_hourly_footfall']
        svi_i = row['store_viability_index']

        primary_sensors = []
        secondary_sensors = []
        tertiary_sensors = []
        gravity_accessibility = 0.0

        for jdx, other in df.iterrows():
            if idx == jdx:
                continue
            lat_j, lon_j = other['latitude'], other['longitude']
            vol_j = other['avg_hourly_footfall']
            dist_m = haversine_distance_meters(lat_i, lon_i, lat_j, lon_j)

            # Spatial gravity index: V_j / (dist_km ^ beta)
            dist_km = max(dist_m / 1000.0, 0.05)  # clamp at 50m to avoid singularity
            gravity_accessibility += vol_j / (dist_km ** BETA_DECAY)

            if dist_m <= R_PRIMARY:
                primary_sensors.append((other['sensor_id'], vol_j, dist_m))
            elif dist_m <= R_SECONDARY:
                secondary_sensors.append((other['sensor_id'], vol_j, dist_m))
            elif dist_m <= R_TERTIARY:
                tertiary_sensors.append((other['sensor_id'], vol_j, dist_m))

        # Catchment footfall pool estimation
        primary_footfall_pool = sum([s[1] for s in primary_sensors]) + vol_i
        secondary_footfall_pool = sum([s[1] for s in secondary_sensors])
        tertiary_footfall_pool = sum([s[1] for s in tertiary_sensors])

        # Effective Pedestrian Capture Potential (60% primary, 25% secondary, 10% tertiary)
        effective_capture_potential = (
            0.60 * primary_footfall_pool +
            0.25 * secondary_footfall_pool +
            0.10 * tertiary_footfall_pool
        )

        results.append({
            'sensor_id': sensor_id,
            'sensor_name': sensor_name,
            'precinct_name': precinct,
            'latitude': lat_i,
            'longitude': lon_i,
            'store_viability_index': svi_i,
            'avg_hourly_footfall': vol_i,
            'primary_catchment_sensor_count': len(primary_sensors),
            'primary_footfall_pool': round(primary_footfall_pool, 1),
            'secondary_catchment_sensor_count': len(secondary_sensors),
            'secondary_footfall_pool': round(secondary_footfall_pool, 1),
            'tertiary_catchment_sensor_count': len(tertiary_sensors),
            'tertiary_footfall_pool': round(tertiary_footfall_pool, 1),
            'effective_capture_potential': round(effective_capture_potential, 1),
            'spatial_gravity_accessibility': round(gravity_accessibility, 2)
        })

    df_out = pd.DataFrame(results)

    # Rank by effective capture potential
    df_out['catchment_rank'] = df_out['effective_capture_potential'].rank(ascending=False, method='dense').astype(int)
    df_out = df_out.sort_values(by='catchment_rank', ascending=True)

    # Save to CSV
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_out.to_csv(OUTPUT_CATCHMENT_CSV, index=False)
    print(f"Pedestrian Catchment Isochrones saved to: {OUTPUT_CATCHMENT_CSV}")

    # Summary statistics
    summary = {
        "analysis_name": "GeoPulse Pedestrian Catchment Isochrones & Gravity Model",
        "total_catchments_evaluated": len(df_out),
        "isochrone_parameters": {
            "primary_radius_m": R_PRIMARY,
            "secondary_radius_m": R_SECONDARY,
            "tertiary_radius_m": R_TERTIARY,
            "gravity_decay_beta": BETA_DECAY
        },
        "mean_effective_capture_potential": round(float(df_out['effective_capture_potential'].mean()), 2),
        "top_5_catchment_hubs": df_out.head(5)[[
            'catchment_rank', 'sensor_name', 'precinct_name', 'effective_capture_potential', 'store_viability_index'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_GRAVITY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Catchment gravity summary saved to: {OUTPUT_GRAVITY_JSON}")

    print("\n--- TOP 3 PEDESTRIAN CATCHMENT HUBS BY EFFECTIVE CAPTURE ---")
    for hub in summary['top_5_catchment_hubs'][:3]:
        print(f"Rank {hub['catchment_rank']}: {hub['sensor_name']} ({hub['precinct_name']}) - Capture Potential: {hub['effective_capture_potential']} (SVI: {hub['store_viability_index']})")

    return df_out

if __name__ == '__main__':
    compute_pedestrian_catchments()
