"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Retail Rent Sensitivity & Turnover Elasticity Simulator
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
OUTPUT_SENSITIVITY_CSV = os.path.join(REPORTS_DIR, "rent_sensitivity_simulation.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "rent_elasticity_summary.json")

def simulate_rent_sensitivity():
    print("=" * 70)
    print("GeoPulse: Simulating Retail Rent Sensitivity & Turnover Elasticity")
    print("=" * 70)

    if not os.path.exists(SVI_CSV) or not os.path.exists(MONETIZATION_CSV):
        raise FileNotFoundError("Missing prerequisite CSV reports. Run previous modules first.")

    df_svi = pd.read_csv(SVI_CSV)
    df_mon = pd.read_csv(MONETIZATION_CSV)[[
        'sensor_id', 'recommended_tenant', 'estimated_annual_turnover_aud',
        'sustainable_annual_rent_aud', 'rent_per_sqm_annual_aud'
    ]]

    df = df_svi.merge(df_mon, on='sensor_id', how='left')

    simulation_records = []

    # Footfall stress levels: -30%, -15%, Baseline (0%), +15%, +30%
    STRESS_LEVELS = [-0.30, -0.15, 0.0, 0.15, 0.30]

    for _, row in df.iterrows():
        sid = row['sensor_id']
        name = row['sensor_name']
        precinct = row['precinct_name']
        svi = row['store_viability_index']
        tenant = row['recommended_tenant']
        base_gmv = row['estimated_annual_turnover_aud']
        base_rent = row['sustainable_annual_rent_aud']
        rent_sqm = row['rent_per_sqm_annual_aud']

        # Determine Break-Even Footfall:
        # If Occupancy Cost Ratio (OCR) exceeds 18%, store enters critical lease stress
        # GMV_min = base_rent / 0.18
        break_even_gmv = base_rent / 0.18
        break_even_footfall_ratio = break_even_gmv / max(base_gmv, 1.0)
        break_even_hourly_footfall = row['avg_hourly_footfall'] * break_even_footfall_ratio

        # Evaluate sensitivity under stress scenarios
        gmv_down_30 = base_gmv * 0.70
        ocr_down_30 = (base_rent / max(gmv_down_30, 1.0)) * 100.0

        gmv_up_30 = base_gmv * 1.30
        ocr_up_30 = (base_rent / max(gmv_up_30, 1.0)) * 100.0

        # Turnover Percentage Rent Model (Base rent 70% + 8% turnover over breakpoint)
        breakpoint_sales = base_gmv * 0.85
        turnover_rent_down_30 = (base_rent * 0.70) + max(0, (gmv_down_30 - breakpoint_sales) * 0.08)
        turnover_rent_up_30 = (base_rent * 0.70) + max(0, (gmv_up_30 - breakpoint_sales) * 0.08)

        # Lease Structure Recommendation
        if svi >= 75.0:
            recommended_lease = "Fixed Base Lease (High landlord pricing power & strong tenant demand)"
        elif svi >= 60.0:
            recommended_lease = "Hybrid Base + Turnover Rent (Shared upside, protected floor)"
        else:
            recommended_lease = "Turnover-Linked Concession (High volatility mitigation for tenant)"

        simulation_records.append({
            'sensor_id': sid,
            'sensor_name': name,
            'precinct_name': precinct,
            'store_viability_index': svi,
            'recommended_tenant': tenant,
            'baseline_annual_gmv_aud': round(base_gmv, 2),
            'baseline_annual_rent_aud': round(base_rent, 2),
            'rent_per_sqm_aud': round(rent_sqm, 2),
            'break_even_hourly_footfall': round(break_even_hourly_footfall, 1),
            'ocr_at_minus_30pct_footfall': round(ocr_down_30, 2),
            'ocr_at_plus_30pct_footfall': round(ocr_up_30, 2),
            'hybrid_rent_at_minus_30pct': round(turnover_rent_down_30, 2),
            'hybrid_rent_at_plus_30pct': round(turnover_rent_up_30, 2),
            'recommended_lease_structure': recommended_lease
        })

    df_out = pd.DataFrame(simulation_records)
    df_out = df_out.sort_values(by='store_viability_index', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_out.to_csv(OUTPUT_SENSITIVITY_CSV, index=False)
    print(f"Rent sensitivity simulation saved to: {OUTPUT_SENSITIVITY_CSV}")

    # Summary
    lease_counts = df_out['recommended_lease_structure'].value_counts().to_dict()
    summary = {
        "analysis_name": "GeoPulse Retail Rent Sensitivity & Turnover Elasticity",
        "total_locations_simulated": len(df_out),
        "mean_break_even_hourly_footfall": round(float(df_out['break_even_hourly_footfall'].mean()), 1),
        "mean_ocr_at_minus_30pct": round(float(df_out['ocr_at_minus_30pct_footfall'].mean()), 2),
        "mean_ocr_at_plus_30pct": round(float(df_out['ocr_at_plus_30pct_footfall'].mean()), 2),
        "recommended_lease_distribution": lease_counts,
        "sample_flagship_lease_simulations": df_out.head(5)[[
            'sensor_name', 'precinct_name', 'store_viability_index', 'recommended_lease_structure',
            'baseline_annual_rent_aud', 'break_even_hourly_footfall'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Rent elasticity summary saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- RECOMMENDED LEASE STRUCTURE DISTRIBUTION ---")
    for lease, count in lease_counts.items():
        print(f"  • {lease}: {count} sites ({count/len(df_out)*100:.1f}%)")

    return df_out

if __name__ == '__main__':
    simulate_rent_sensitivity()
