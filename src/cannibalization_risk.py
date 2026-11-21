"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Store Cannibalization Risk & Co-Location Competition Analyzer
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
OUTPUT_CANNIBALIZATION_CSV = os.path.join(REPORTS_DIR, "store_cannibalization_risk.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "cannibalization_summary.json")

def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance in meters."""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def analyze_cannibalization_risk():
    print("=" * 70)
    print("GeoPulse: Analyzing Store Cannibalization & Co-Location Competition Risk")
    print("=" * 70)

    if not os.path.exists(SVI_CSV):
        raise FileNotFoundError(f"Missing {SVI_CSV}. Run store_viability_index.py first.")

    df = pd.read_csv(SVI_CSV)
    print(f"Loaded {len(df)} retail sensor nodes.")

    # Critical threshold for pedestrian overlap: 350 meters
    DISTANCE_THRESHOLD_M = 350.0
    DECAY_SCALE_M = 200.0

    pair_results = []
    n = len(df)

    for i in range(n):
        node_a = df.iloc[i]
        for j in range(i + 1, n):
            node_b = df.iloc[j]

            dist_m = haversine_distance_meters(
                node_a['latitude'], node_a['longitude'],
                node_b['latitude'], node_b['longitude']
            )

            if dist_m <= DISTANCE_THRESHOLD_M:
                vol_a = node_a['avg_hourly_footfall']
                vol_b = node_b['avg_hourly_footfall']

                # Parity ratio: min / max
                vol_min = min(vol_a, vol_b)
                vol_max = max(vol_a, vol_b)
                parity = vol_min / vol_max if vol_max > 0 else 0

                # Cannibalization Risk Index (CRI): 0 to 100 scale
                spatial_decay = math.exp(-dist_m / DECAY_SCALE_M)
                cri = round(100.0 * math.sqrt(parity) * spatial_decay, 2)

                # Risk Classification
                if cri >= 60.0:
                    risk_tier = "Critical Cannibalization Risk"
                    recommendation = "Enforce single-store exclusivity; avoid sister franchise deployment within 300m"
                elif cri >= 35.0:
                    risk_tier = "Moderate Catchment Overlap"
                    recommendation = "Differentiate store formats (e.g., Flagship vs. Express Grab-and-Go)"
                else:
                    risk_tier = "Low / Synergistic Co-location"
                    recommendation = "Complementary footfall capture; cross-promotional retail viable"

                pair_results.append({
                    'sensor_a_id': int(node_a['sensor_id']),
                    'sensor_a_name': node_a['sensor_name'],
                    'sensor_a_precinct': node_a['precinct_name'],
                    'sensor_b_id': int(node_b['sensor_id']),
                    'sensor_b_name': node_b['sensor_name'],
                    'sensor_b_precinct': node_b['precinct_name'],
                    'distance_meters': round(dist_m, 1),
                    'footfall_a': round(vol_a, 1),
                    'footfall_b': round(vol_b, 1),
                    'cannibalization_risk_index': cri,
                    'risk_tier': risk_tier,
                    'recommendation': recommendation
                })

    df_pairs = pd.DataFrame(pair_results)
    if not df_pairs.empty:
        df_pairs = df_pairs.sort_values(by='cannibalization_risk_index', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_pairs.to_csv(OUTPUT_CANNIBALIZATION_CSV, index=False)
    print(f"Store Cannibalization Risk report saved to: {OUTPUT_CANNIBALIZATION_CSV}")

    # Aggregated Summary
    critical_count = len(df_pairs[df_pairs['risk_tier'] == "Critical Cannibalization Risk"])
    moderate_count = len(df_pairs[df_pairs['risk_tier'] == "Moderate Catchment Overlap"])
    low_count = len(df_pairs[df_pairs['risk_tier'] == "Low / Synergistic Co-location"])

    summary = {
        "analysis_name": "GeoPulse Spatial Cannibalization & Co-Location Risk Engine",
        "overlap_threshold_meters": DISTANCE_THRESHOLD_M,
        "total_overlapping_pairs_identified": len(df_pairs),
        "risk_tier_distribution": {
            "critical_cannibalization_risk": critical_count,
            "moderate_catchment_overlap": moderate_count,
            "low_synergistic_co_location": low_count
        },
        "top_5_critical_cannibalization_pairs": df_pairs.head(5)[[
            'sensor_a_name', 'sensor_b_name', 'distance_meters', 'cannibalization_risk_index', 'risk_tier'
        ]].to_dict(orient='records') if not df_pairs.empty else []
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Cannibalization summary saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- TOP 3 CRITICAL CANNIBALIZATION PAIRS ---")
    for p in summary['top_5_critical_cannibalization_pairs'][:3]:
        print(f"• {p['sensor_a_name']} <--> {p['sensor_b_name']} ({p['distance_meters']}m) - CRI: {p['cannibalization_risk_index']} [{p['risk_tier']}]")

    return df_pairs

if __name__ == '__main__':
    analyze_cannibalization_risk()
