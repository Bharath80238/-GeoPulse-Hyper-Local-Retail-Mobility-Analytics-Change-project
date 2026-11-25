"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Store Expansion Optimizer & Non-Cannibalizing Portfolio Planner
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
MONETIZATION_CSV = os.path.join(REPORTS_DIR, "catchment_monetization_estimates.csv")
OUTPUT_EXPANSION_CSV = os.path.join(REPORTS_DIR, "store_expansion_portfolios.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "expansion_optimizer_summary.json")

def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance in meters."""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def solve_expansion_portfolio(df_candidates, target_k, min_distance_m, max_per_precinct):
    """
    Greedy Facility Location Optimization with Spatial Exclusion Radius.
    Maximizes combined SVI while enforcing minimum spatial separation to prevent cannibalization.
    """
    selected = []
    candidates = df_candidates.sort_values(by='expansion_priority_score', ascending=False).to_dict(orient='records')
    precinct_counts = {}

    for cand in candidates:
        if len(selected) >= target_k:
            break

        cand_precinct = cand['precinct_name']
        if precinct_counts.get(cand_precinct, 0) >= max_per_precinct:
            continue

        # Check spatial separation against already selected stores
        is_separated = True
        for sel in selected:
            dist = haversine_distance_meters(
                cand['latitude'], cand['longitude'],
                sel['latitude'], sel['longitude']
            )
            if dist < min_distance_m:
                is_separated = False
                break

        if is_separated:
            selected.append(cand)
            precinct_counts[cand_precinct] = precinct_counts.get(cand_precinct, 0) + 1

    return selected

def optimize_store_expansion():
    print("=" * 70)
    print("GeoPulse: Optimizing Retail Store Expansion & Non-Cannibalizing Portfolios")
    print("=" * 70)

    if not os.path.exists(SVI_CSV) or not os.path.exists(MONETIZATION_CSV):
        raise FileNotFoundError("Prerequisite CSV reports missing. Run previous pipelines first.")

    df_svi = pd.read_csv(SVI_CSV)
    df_mon = pd.read_csv(MONETIZATION_CSV)[['sensor_id', 'estimated_annual_turnover_aud']]

    df = df_svi.merge(df_mon, on='sensor_id', how='left')

    # Expansion Priority Score = SVI * log(1 + Footfall)
    df['expansion_priority_score'] = df['store_viability_index'] * np.log1p(df['avg_hourly_footfall'])

    # Solve 3 Strategic Portfolios:
    # Portfolio A: 3-Store Luxury / Flagship Rollout (Min distance 500m, max 1 per precinct)
    # Portfolio B: 5-Store Fast Casual / QSR Network (Min distance 400m, max 2 per precinct)
    # Portfolio C: 8-Store Convenience Footprint (Min distance 300m, max 3 per precinct)

    portfolio_a = solve_expansion_portfolio(df, target_k=3, min_distance_m=500.0, max_per_precinct=1)
    portfolio_b = solve_expansion_portfolio(df, target_k=5, min_distance_m=400.0, max_per_precinct=2)
    portfolio_c = solve_expansion_portfolio(df, target_k=8, min_distance_m=300.0, max_per_precinct=3)

    records = []
    for plan_name, plan_data in [
        ("Portfolio A: 3-Store Flagship Rollout", portfolio_a),
        ("Portfolio B: 5-Store Fast Casual Network", portfolio_b),
        ("Portfolio C: 8-Store Convenience Footprint", portfolio_c)
    ]:
        for rank_idx, s in enumerate(plan_data, 1):
            records.append({
                'portfolio_plan': plan_name,
                'store_sequence_rank': rank_idx,
                'sensor_id': s['sensor_id'],
                'sensor_name': s['sensor_name'],
                'precinct_name': s['precinct_name'],
                'store_viability_index': s['store_viability_index'],
                'avg_hourly_footfall': s['avg_hourly_footfall'],
                'estimated_annual_turnover_aud': s['estimated_annual_turnover_aud'],
                'latitude': s['latitude'],
                'longitude': s['longitude']
            })

    df_export = pd.DataFrame(records)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_export.to_csv(OUTPUT_EXPANSION_CSV, index=False)
    print(f"Store expansion portfolios saved to: {OUTPUT_EXPANSION_CSV}")

    # Summary
    def summarize_plan(plan_records):
        return {
            "store_count": len(plan_records),
            "mean_svi": round(float(np.mean([p['store_viability_index'] for p in plan_records])), 2),
            "total_network_annual_gmv_aud": round(float(np.sum([p['estimated_annual_turnover_aud'] for p in plan_records])), 2),
            "precincts_covered": list(set([p['precinct_name'] for p in plan_records])),
            "stores": [f"{p['sensor_name']} ({p['precinct_name']})" for p in plan_records]
        }

    summary = {
        "analysis_name": "GeoPulse Strategic Store Expansion Optimization",
        "portfolio_a_flagship_3store": summarize_plan(portfolio_a),
        "portfolio_b_fast_casual_5store": summarize_plan(portfolio_b),
        "portfolio_c_convenience_8store": summarize_plan(portfolio_c)
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Expansion optimizer summary saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- OPTIMAL 3-STORE STRATEGIC FLAGSHIP ROLLOUT ---")
    for s in summary['portfolio_a_flagship_3store']['stores']:
        print(f"  ★ Store: {s}")
    print(f"  Combined GMV Potential: ${summary['portfolio_a_flagship_3store']['total_network_annual_gmv_aud']:,.2f} AUD")

    return df_export

if __name__ == '__main__':
    optimize_store_expansion()
