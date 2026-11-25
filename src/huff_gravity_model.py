"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Huff Gravity Model & Retail Precinct Market Share Simulator
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
PRECINCT_JSON = os.path.join(REPORTS_DIR, "retail_precinct_summary.json")
OUTPUT_HUFF_CSV = os.path.join(REPORTS_DIR, "huff_market_share_probabilities.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "huff_model_summary.json")

def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance in meters."""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def compute_huff_model():
    print("=" * 70)
    print("GeoPulse: Computing Huff Gravity Model & Precinct Market Share")
    print("=" * 70)

    if not os.path.exists(SVI_CSV):
        raise FileNotFoundError(f"Missing {SVI_CSV}. Run store_viability_index.py first.")

    df_svi = pd.read_csv(SVI_CSV)
    print(f"Loaded {len(df_svi)} sensor locations.")

    # 1. Establish Precinct Attractiveness Centers (Mass & Centroids)
    precinct_groups = df_svi.groupby('precinct_name').agg(
        sensor_count=('sensor_id', 'count'),
        total_footfall=('avg_hourly_footfall', 'sum'),
        mean_svi=('store_viability_index', 'mean'),
        centroid_lat=('latitude', 'mean'),
        centroid_lon=('longitude', 'mean')
    ).reset_index()

    # Attractiveness Index: Log(total_footfall) * mean_svi
    precinct_groups['attractiveness_mass'] = np.log1p(precinct_groups['total_footfall']) * (precinct_groups['mean_svi'] / 100.0)
    precincts = precinct_groups.to_dict(orient='records')

    # Huff parameters:
    # Alpha = 1.0 (attractiveness elasticity)
    # Lambda = 1.8 (pedestrian distance friction exponent)
    ALPHA = 1.0
    LAMBDA = 1.8

    results = []

    # 2. For each sensor node (origin), compute probability of visiting each commercial precinct
    for _, sensor in df_svi.iterrows():
        lat_i, lon_i = sensor['latitude'], sensor['longitude']
        sensor_id = sensor['sensor_id']
        sensor_name = sensor['sensor_name']
        local_precinct = sensor['precinct_name']
        footfall_pool = sensor['avg_hourly_footfall']

        utilities = []
        for p in precincts:
            dist_m = haversine_distance_meters(lat_i, lon_i, p['centroid_lat'], p['centroid_lon'])
            dist_km = max(dist_m / 1000.0, 0.05)  # clamp at 50m to avoid zero division

            # Utility: S_j^alpha / d_ij^lambda
            utility = (p['attractiveness_mass'] ** ALPHA) / (dist_km ** LAMBDA)
            utilities.append({
                'precinct_name': p['precinct_name'],
                'dist_meters': round(dist_m, 1),
                'utility': utility
            })

        total_utility = sum(u['utility'] for u in utilities)

        # Compute probabilities
        prob_dict = {}
        for u in utilities:
            prob = (u['utility'] / total_utility) if total_utility > 0 else 0.0
            prob_dict[u['precinct_name']] = round(prob, 4)

        # Determine dominant precinct attraction
        dominant_precinct = max(prob_dict, key=prob_dict.get)
        dominant_prob = prob_dict[dominant_precinct]

        row_data = {
            'sensor_id': sensor_id,
            'sensor_name': sensor_name,
            'local_precinct': local_precinct,
            'store_viability_index': sensor['store_viability_index'],
            'avg_hourly_footfall': footfall_pool,
            'dominant_attraction_precinct': dominant_precinct,
            'dominant_capture_probability': dominant_prob,
            'prob_central_retail_core': prob_dict.get('Central Retail Core (Bourke St Mall)', 0.0),
            'prob_flinders_transit': prob_dict.get('Flinders Transit Hub (Commuter Spine)', 0.0),
            'prob_southbank': prob_dict.get('Southbank Promenade & Waterfront', 0.0),
            'prob_docklands': prob_dict.get('Docklands Harbourside', 0.0),
            'prob_chinatown': prob_dict.get('Chinatown & Eastern Dining Precinct', 0.0),
            'prob_university_corridor': prob_dict.get('Northern University & Research Corridor', 0.0)
        }
        results.append(row_data)

    df_huff = pd.DataFrame(results)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_huff.to_csv(OUTPUT_HUFF_CSV, index=False)
    print(f"Huff model probabilities saved to: {OUTPUT_HUFF_CSV}")

    # Summary of simulated market share
    simulated_market_shares = {}
    for p in precinct_groups['precinct_name']:
        col_name = f"prob_{p.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('&', '').replace('__', '_')}"
        matching_cols = [c for c in df_huff.columns if p.split()[0].lower() in c]
        if matching_cols:
            share = df_huff[matching_cols[0]].mean()
            simulated_market_shares[p] = round(float(share * 100.0), 2)

    summary = {
        "analysis_name": "GeoPulse Huff Gravity Retail Market Share Simulation",
        "parameters": {
            "attractiveness_alpha": ALPHA,
            "distance_friction_lambda": LAMBDA
        },
        "precinct_attractiveness_centers": precinct_groups[[
            'precinct_name', 'sensor_count', 'attractiveness_mass'
        ]].to_dict(orient='records'),
        "simulated_citywide_market_shares_pct": simulated_market_shares,
        "sample_capture_probabilities": df_huff.head(5)[[
            'sensor_name', 'local_precinct', 'dominant_attraction_precinct', 'dominant_capture_probability'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Huff model summary saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- SIMULATED PRECINCT MARKET SHARES ---")
    for precinct, share in simulated_market_shares.items():
        print(f"  • {precinct}: {share}% of pedestrian trade flow")

    return df_huff

if __name__ == '__main__':
    compute_huff_model()
