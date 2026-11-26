"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Precinct Comparative Benchmarking Engine & Pricing Power Index
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SVI_CSV = os.path.join(REPORTS_DIR, "store_viability_rankings.csv")
MONETIZATION_CSV = os.path.join(REPORTS_DIR, "catchment_monetization_estimates.csv")
SIMULATION_CSV = os.path.join(REPORTS_DIR, "catchment_scenario_simulation.csv")
OUTPUT_BENCHMARK_CSV = os.path.join(REPORTS_DIR, "precinct_comparative_benchmark.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "precinct_benchmark_summary.json")

def generate_precinct_benchmarks():
    print("=" * 70)
    print("GeoPulse: Compiling Cross-Precinct Comparative Benchmarks & Pricing Power Index")
    print("=" * 70)

    if not os.path.exists(SVI_CSV) or not os.path.exists(MONETIZATION_CSV) or not os.path.exists(SIMULATION_CSV):
        raise FileNotFoundError("Missing prerequisite analytical reports. Run previous modules first.")

    df_svi = pd.read_csv(SVI_CSV)
    df_mon = pd.read_csv(MONETIZATION_CSV)[['sensor_id', 'estimated_annual_turnover_aud', 'sustainable_annual_rent_aud', 'rent_per_sqm_annual_aud']]
    df_sim = pd.read_csv(SIMULATION_CSV)[['sensor_id', 'catchment_resilience_score']]

    df = df_svi.merge(df_mon, on='sensor_id', how='left').merge(df_sim, on='sensor_id', how='left')

    # Aggregate by precinct
    benchmarks = []
    precinct_groups = df.groupby('precinct_name')

    for precinct_name, grp in precinct_groups:
        node_count = len(grp)
        mean_svi = grp['store_viability_index'].mean()
        max_svi = grp['store_viability_index'].max()
        mean_hourly_vol = grp['avg_hourly_footfall'].mean()
        total_precinct_gmv = grp['estimated_annual_turnover_aud'].sum()
        mean_site_gmv = grp['estimated_annual_turnover_aud'].mean()
        mean_rent_sqm = grp['rent_per_sqm_annual_aud'].mean()
        mean_weekend_ratio = grp['weekend_surge_ratio'].mean()
        mean_resilience = grp['catchment_resilience_score'].mean()

        # Landlord Pricing Power Index (PPI, 0-100 scale)
        # Combines SVI, Rent/sqm capability, and shock resilience
        ppi_score = (
            0.40 * mean_svi +
            0.35 * min(100.0, (mean_rent_sqm / 2500.0) * 100.0) +
            0.25 * mean_resilience
        )

        if ppi_score >= 75.0:
            power_tier = "Premium Landlord Market (High pricing leverage / premium leases)"
        elif ppi_score >= 60.0:
            power_tier = "Balanced Commercial Market (Standard market terms / steady yield)"
        else:
            power_tier = "Tenant-Favorable Market (Concessions & flexible rent structures)"

        # Precinct Commercial Classification
        if mean_weekend_ratio > 1.15:
            commercial_role = "Weekend Leisure & Dining Destination"
        elif mean_weekend_ratio < 0.85:
            commercial_role = "Weekday Commuter Spine & Office Conduit"
        else:
            commercial_role = "Omni-Channel 7-Day Retail Core"

        benchmarks.append({
            'precinct_name': precinct_name,
            'active_sensor_count': node_count,
            'mean_store_viability_index': round(mean_svi, 2),
            'peak_sensor_svi': round(max_svi, 2),
            'mean_hourly_footfall': round(mean_hourly_vol, 1),
            'total_precinct_annual_gmv_aud': round(total_precinct_gmv, 2),
            'mean_site_annual_gmv_aud': round(mean_site_gmv, 2),
            'mean_rent_per_sqm_aud': round(mean_rent_sqm, 2),
            'mean_weekend_surge_ratio': round(mean_weekend_ratio, 2),
            'mean_resilience_score': round(mean_resilience, 2),
            'landlord_pricing_power_index': round(ppi_score, 2),
            'pricing_power_tier': power_tier,
            'commercial_role': commercial_role
        })

    df_bench = pd.DataFrame(benchmarks)
    df_bench = df_bench.sort_values(by='landlord_pricing_power_index', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_bench.to_csv(OUTPUT_BENCHMARK_CSV, index=False)
    print(f"Precinct comparative benchmarks saved to: {OUTPUT_BENCHMARK_CSV}")

    # Summary JSON
    summary = {
        "analysis_name": "GeoPulse Precinct Comparative Benchmarking Engine",
        "precincts_benchmarked_count": len(df_bench),
        "total_cbd_turnover_modeled_aud": round(float(df_bench['total_precinct_annual_gmv_aud'].sum()), 2),
        "highest_pricing_power_precinct": df_bench.iloc[0]['precinct_name'],
        "highest_pricing_power_score": float(df_bench.iloc[0]['landlord_pricing_power_index']),
        "precinct_rankings": df_bench[[
            'precinct_name', 'active_sensor_count', 'mean_store_viability_index',
            'mean_rent_per_sqm_aud', 'landlord_pricing_power_index', 'pricing_power_tier'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Precinct benchmark summary JSON saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- PRECINCT PRICING POWER RANKINGS ---")
    for idx, r in df_bench.iterrows():
        print(f"  Rank: {r['precinct_name']} | PPI: {r['landlord_pricing_power_index']} ({r['pricing_power_tier'].split('(')[0].strip()})")

    return df_bench

if __name__ == '__main__':
    generate_precinct_benchmarks()
