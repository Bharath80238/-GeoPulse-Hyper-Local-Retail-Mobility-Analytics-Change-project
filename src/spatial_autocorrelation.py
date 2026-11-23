"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Spatial Autocorrelation & Local Moran's I Cluster Detection
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
OUTPUT_LISA_CSV = os.path.join(REPORTS_DIR, "spatial_autocorrelation_lisa.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "morans_i_summary.json")

def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance in meters."""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def compute_spatial_autocorrelation():
    print("=" * 70)
    print("GeoPulse: Computing Spatial Autocorrelation & Local Moran's I (LISA)")
    print("=" * 70)

    if not os.path.exists(SVI_CSV):
        raise FileNotFoundError(f"Missing {SVI_CSV}. Run store_viability_index.py first.")

    df = pd.read_csv(SVI_CSV)
    n = len(df)
    print(f"Loaded {n} retail sensor nodes for spatial dependency analysis.")

    # Variable of interest: Log-transformed average hourly footfall
    y = np.log1p(df['avg_hourly_footfall'].values)
    y_mean = np.mean(y)
    y_dev = y - y_mean
    s2 = np.sum(y_dev ** 2) / n

    # Construct spatial weight matrix using inverse-distance with bandwidth threshold
    # Bandwidth: 600 meters (walking neighborhood)
    BANDWIDTH_M = 600.0
    W = np.zeros((n, n))

    for i in range(n):
        lat_i, lon_i = df.iloc[i]['latitude'], df.iloc[i]['longitude']
        for j in range(n):
            if i == j:
                continue
            lat_j, lon_j = df.iloc[j]['latitude'], df.iloc[j]['longitude']
            dist_m = haversine_distance_meters(lat_i, lon_i, lat_j, lon_j)
            if dist_m <= BANDWIDTH_M:
                # Inverse distance weight
                W[i, j] = 1.0 / max(dist_m, 20.0)

    # Row-standardize weight matrix W
    row_sums = W.sum(axis=1)
    for i in range(n):
        if row_sums[i] > 0:
            W[i, :] = W[i, :] / row_sums[i]

    # Compute Global Moran's I
    # I = (n / S0) * sum_i sum_j (w_ij * (y_i - y_mean) * (y_j - y_mean)) / sum_i (y_i - y_mean)^2
    S0 = np.sum(W)
    numerator = 0.0
    for i in range(n):
        for j in range(n):
            numerator += W[i, j] * y_dev[i] * y_dev[j]

    global_morans_i = (n / S0) * (numerator / np.sum(y_dev ** 2)) if S0 > 0 else 0.0
    expected_i = -1.0 / (n - 1)

    print(f"Global Moran's I: {global_morans_i:.4f} (Expected under randomness: {expected_i:.4f})")
    spatial_pattern = "Positive Spatial Clustering (Commercial Agglomeration)" if global_morans_i > expected_i else "Spatial Dispersion"

    # Compute Local Moran's I (LISA) for each sensor
    # I_i = (y_i - y_mean) / s2 * sum_j (w_ij * (y_j - y_mean))
    local_I = np.zeros(n)
    spatial_lag = np.zeros(n)
    lisa_clusters = []

    for i in range(n):
        lag_i = np.sum(W[i, :] * y_dev)
        spatial_lag[i] = lag_i
        local_I[i] = (y_dev[i] / s2) * lag_i if s2 > 0 else 0.0

        # LISA Quadrant Classification:
        # High-High (Hotspot): high value surrounded by high values
        # Low-Low (Coldspot): low value surrounded by low values
        # High-Low (Spatial Outlier): high value surrounded by low values
        # Low-High (Spatial Outlier): low value surrounded by high values
        is_high_val = y_dev[i] >= 0
        is_high_lag = lag_i >= 0

        if is_high_val and is_high_lag:
            cluster_type = "High-High (Prime Retail Hotspot)"
        elif not is_high_val and not is_high_lag:
            cluster_type = "Low-Low (Peripheral Coldspot)"
        elif is_high_val and not is_high_lag:
            cluster_type = "High-Low (Isolated Retail Island)"
        else:
            cluster_type = "Low-High (Underperforming Corridor Island)"

        lisa_clusters.append(cluster_type)

    # Compile Results
    df_lisa = df.copy()
    df_lisa['local_morans_i'] = np.round(local_I, 4)
    df_lisa['spatial_lag_y'] = np.round(spatial_lag, 4)
    df_lisa['lisa_cluster'] = lisa_clusters

    # Actionable retail recommendation based on LISA
    def get_lisa_recommendation(cluster):
        if "High-High" in cluster:
            return "High commercial gravity; ideal for flagship luxury, anchor stores, and high capex formats"
        elif "Low-Low" in cluster:
            return "Low traffic basin; suited for destination services, dark kitchens, or non-retail functions"
        elif "High-Low" in cluster:
            return "Distinctive destination anchor; captures monopoly pedestrian share without nearby competition"
        else:
            return "Retail arbitrage opportunity; benefits from neighboring traffic spillover with lower rent potential"

    df_lisa['retail_spatial_action'] = df_lisa['lisa_cluster'].apply(get_lisa_recommendation)

    export_cols = [
        'sensor_id', 'sensor_name', 'precinct_name', 'store_viability_index',
        'avg_hourly_footfall', 'local_morans_i', 'lisa_cluster', 'retail_spatial_action'
    ]
    df_export = df_lisa[export_cols]

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_export.to_csv(OUTPUT_LISA_CSV, index=False)
    print(f"LISA spatial autocorrelation saved to: {OUTPUT_LISA_CSV}")

    # Summary
    cluster_counts = df_export['lisa_cluster'].value_counts().to_dict()
    summary = {
        "analysis_name": "GeoPulse Spatial Autocorrelation & LISA Cluster Analysis",
        "spatial_parameters": {
            "bandwidth_meters": BANDWIDTH_M,
            "weighting_method": "Row-standardized inverse distance",
            "variable_tested": "log1p(avg_hourly_footfall)"
        },
        "global_morans_i": round(float(global_morans_i), 4),
        "expected_morans_i": round(float(expected_i), 4),
        "overall_spatial_pattern": spatial_pattern,
        "lisa_cluster_distribution": cluster_counts,
        "sample_hotspots": df_export[df_export['lisa_cluster'] == "High-High (Prime Retail Hotspot)"].head(5)[
            ['sensor_name', 'precinct_name', 'store_viability_index', 'avg_hourly_footfall']
        ].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Moran's I summary saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- LISA SPATIAL CLUSTER BREAKDOWN ---")
    for cluster, count in cluster_counts.items():
        print(f"  • {cluster}: {count} locations ({count/n*100:.1f}%)")

    return df_export

if __name__ == '__main__':
    compute_spatial_autocorrelation()
