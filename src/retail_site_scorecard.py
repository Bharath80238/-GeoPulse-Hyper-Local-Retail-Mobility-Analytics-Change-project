"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Master Retail Site Selection Scorecard & Consolidated Matrix
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

OUTPUT_SCORECARD_CSV = os.path.join(REPORTS_DIR, "master_retail_site_scorecard.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "scorecard_summary.json")

def generate_master_scorecard():
    print("=" * 70)
    print("GeoPulse: Compiling Master Retail Site Selection Scorecard")
    print("=" * 70)

    # Load core tables
    svi_df = pd.read_csv(os.path.join(REPORTS_DIR, "store_viability_rankings.csv"))
    lisa_df = pd.read_csv(os.path.join(REPORTS_DIR, "spatial_autocorrelation_lisa.csv"))[['sensor_id', 'local_morans_i', 'lisa_cluster']]
    isochrone_df = pd.read_csv(os.path.join(REPORTS_DIR, "pedestrian_catchment_radii.csv"))[['sensor_id', 'effective_capture_potential', 'spatial_gravity_accessibility']]
    cannibal_df = pd.read_csv(os.path.join(REPORTS_DIR, "store_cannibalization_risk.csv"))
    tenant_df = pd.read_csv(os.path.join(REPORTS_DIR, "tenant_site_recommendations.csv"))[['sensor_id', 'primary_recommended_tenant', 'strategic_rationale']]
    monetization_df = pd.read_csv(os.path.join(REPORTS_DIR, "catchment_monetization_estimates.csv"))[['sensor_id', 'estimated_annual_turnover_aud', 'rent_per_sqm_annual_aud']]
    simulation_df = pd.read_csv(os.path.join(REPORTS_DIR, "catchment_scenario_simulation.csv"))[['sensor_id', 'catchment_resilience_score', 'resilience_tier']]

    # Calculate max cannibalization risk per sensor
    cannibal_hazard = {}
    for sid in svi_df['sensor_id']:
        matches = cannibal_df[(cannibal_df['sensor_a_id'] == sid) | (cannibal_df['sensor_b_id'] == sid)]
        if not matches.empty:
            max_cri = matches['cannibalization_risk_index'].max()
            cannibal_hazard[sid] = max_cri
        else:
            cannibal_hazard[sid] = 0.0

    # Merge into master dataframe
    df = svi_df.merge(lisa_df, on='sensor_id', how='left')
    df = df.merge(isochrone_df, on='sensor_id', how='left')
    df = df.merge(tenant_df, on='sensor_id', how='left')
    df = df.merge(monetization_df, on='sensor_id', how='left')
    df = df.merge(simulation_df, on='sensor_id', how='left')

    df['max_cannibalization_risk'] = df['sensor_id'].map(cannibal_hazard).fillna(0.0)
    df['cannibalization_alert'] = df['max_cannibalization_risk'].apply(lambda x: "High Conflict Hazard" if x >= 60.0 else ("Moderate Overlap" if x >= 35.0 else "Clear / Low Conflict"))

    # Final Corporate Real Estate Recommendation
    def determine_site_decision(row):
        svi = row['store_viability_index']
        resilience = row['catchment_resilience_score']
        cannibal = row['max_cannibalization_risk']
        cluster = str(row['lisa_cluster'])

        if svi >= 75.0 and cannibal < 60.0 and resilience >= 65.0:
            return "Tier 1 Priority Anchor (Immediate Lease Acquisition)"
        elif svi >= 70.0 and "High-High" in cluster:
            return "Strategic Core Investment (Differentiate Store Concept)"
        elif svi >= 60.0 and resilience >= 60.0:
            return "Viable Growth Location (Standard Retail Lease)"
        elif cannibal >= 75.0:
            return "High Cannibalization Hazard (Enforce Territory Buffer)"
        elif svi < 50.0:
            return "Non-Prime / Peripheral (Selective Concession Only)"
        else:
            return "Conditional Viability (Perform Secondary Traffic Audit)"

    df['executive_decision'] = df.apply(determine_site_decision, axis=1)

    export_cols = [
        'rank',
        'sensor_id',
        'sensor_name',
        'precinct_name',
        'store_viability_index',
        'viability_tier',
        'lisa_cluster',
        'effective_capture_potential',
        'primary_recommended_tenant',
        'estimated_annual_turnover_aud',
        'rent_per_sqm_annual_aud',
        'catchment_resilience_score',
        'max_cannibalization_risk',
        'cannibalization_alert',
        'executive_decision'
    ]
    df_export = df[export_cols]

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_export.to_csv(OUTPUT_SCORECARD_CSV, index=False)
    print(f"Master Retail Site Scorecard saved to: {OUTPUT_SCORECARD_CSV}")

    # Summary
    decisions_count = df_export['executive_decision'].value_counts().to_dict()
    summary = {
        "analysis_name": "GeoPulse Master Retail Site Selection Scorecard",
        "total_sites_scored": len(df_export),
        "mean_svi": round(float(df_export['store_viability_index'].mean()), 2),
        "total_estimated_turnover_aud": round(float(df_export['estimated_annual_turnover_aud'].sum()), 2),
        "executive_decision_distribution": decisions_count,
        "priority_sites": df_export[df_export['executive_decision'].str.contains("Priority")][[
            'rank', 'sensor_name', 'precinct_name', 'store_viability_index', 'estimated_annual_turnover_aud'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Scorecard summary saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- EXECUTIVE SITE DECISION DISTRIBUTION ---")
    for dec, count in decisions_count.items():
        print(f"  • {dec}: {count} sites ({count/len(df_export)*100:.1f}%)")

    return df_export

if __name__ == '__main__':
    generate_master_scorecard()
