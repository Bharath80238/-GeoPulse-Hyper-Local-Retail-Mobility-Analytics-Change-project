"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Catchment Monetization & Store Turnover Revenue Estimator
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
TENANT_CSV = os.path.join(REPORTS_DIR, "tenant_site_recommendations.csv")
OUTPUT_MONETIZATION_CSV = os.path.join(REPORTS_DIR, "catchment_monetization_estimates.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "monetization_summary.json")

# Commercial parameters by tenant archetype
TENANT_ECONOMICS = {
    "Luxury / Flagship Brand": {
        "conversion_rate": 0.015,     # 1.5% store walk-in conversion
        "avg_transaction_value": 185.0, # High ticket AUD
        "occupancy_cost_ratio": 0.15   # Max rent as % of GMV
    },
    "QSR / Grab-and-Go": {
        "conversion_rate": 0.045,     # 4.5% high impulse conversion
        "avg_transaction_value": 16.5, # Fast casual ticket AUD
        "occupancy_cost_ratio": 0.12
    },
    "Experiential Dining / Nightlife": {
        "conversion_rate": 0.025,
        "avg_transaction_value": 68.0,
        "occupancy_cost_ratio": 0.14
    },
    "Convenience Retail / Essential Services": {
        "conversion_rate": 0.055,     # 5.5% necessity walk-in
        "avg_transaction_value": 14.0,
        "occupancy_cost_ratio": 0.10
    },
    "Artisan Boutique / Specialty Retail": {
        "conversion_rate": 0.020,
        "avg_transaction_value": 45.0,
        "occupancy_cost_ratio": 0.13
    }
}

def estimate_catchment_monetization():
    print("=" * 70)
    print("GeoPulse: Estimating Retail Catchment Turnover & Rental Affordability")
    print("=" * 70)

    if not os.path.exists(SVI_CSV) or not os.path.exists(TENANT_CSV):
        raise FileNotFoundError("Missing prerequisite SVI or Tenant CSV reports. Run prior modules first.")

    df_svi = pd.read_csv(SVI_CSV)
    df_tenant = pd.read_csv(TENANT_CSV)[['sensor_id', 'primary_recommended_tenant', 'strategic_rationale']]

    df = df_svi.merge(df_tenant, on='sensor_id', how='left')
    df['primary_recommended_tenant'] = df['primary_recommended_tenant'].fillna("Artisan Boutique / Specialty Retail")

    results = []

    for _, row in df.iterrows():
        tenant_type = row['primary_recommended_tenant']
        econ = TENANT_ECONOMICS.get(tenant_type, TENANT_ECONOMICS["Artisan Boutique / Specialty Retail"])

        # Footfall conversions (Assuming active 16-hour daily commercial trading window)
        hourly_footfall = row['avg_hourly_footfall']
        daily_pedestrian_traffic = hourly_footfall * 16.0
        monthly_pedestrian_traffic = daily_pedestrian_traffic * 30.4  # avg days per month

        # Retail Conversion Funnel
        conv_rate = econ['conversion_rate']
        atv = econ['avg_transaction_value']
        ocr = econ['occupancy_cost_ratio']

        # SVI multiplier modifier (+/- 15% efficiency boost for high SVI sites)
        svi_modifier = 0.85 + (row['store_viability_index'] / 100.0) * 0.30

        monthly_paying_customers = monthly_pedestrian_traffic * conv_rate * svi_modifier
        estimated_monthly_turnover = monthly_paying_customers * atv
        estimated_annual_turnover = estimated_monthly_turnover * 12.0

        # Maximum Sustainable Rent (Occupancy Cost)
        sustainable_annual_rent = estimated_annual_turnover * ocr
        sustainable_monthly_rent = sustainable_annual_rent / 12.0

        # Rent per sqm estimate (Assuming standard 80 sqm standard CBD retail footprint)
        estimated_rent_per_sqm_annual = sustainable_annual_rent / 80.0

        # Arbitrage classification
        if row['store_viability_index'] >= 70.0 and estimated_rent_per_sqm_annual >= 2500:
            arbitrage_tier = "Prime High-Yield Anchor (Maximum Commercial Rent Capacity)"
        elif row['store_viability_index'] >= 60.0:
            arbitrage_tier = "Growth Commercial Hub (Strong Sales-to-Rent Profile)"
        elif row['store_viability_index'] >= 50.0:
            arbitrage_tier = "Moderate Neighborhood Yield (Standard Retail Lease)"
        else:
            arbitrage_tier = "Value / Concession Zone (Flexible / Turnover-Linked Rent)"

        results.append({
            'sensor_id': row['sensor_id'],
            'sensor_name': row['sensor_name'],
            'precinct_name': row['precinct_name'],
            'viability_tier': row['viability_tier'],
            'store_viability_index': row['store_viability_index'],
            'avg_hourly_footfall': round(hourly_footfall, 1),
            'recommended_tenant': tenant_type,
            'monthly_pedestrian_traffic': int(monthly_pedestrian_traffic),
            'monthly_paying_customers': int(monthly_paying_customers),
            'estimated_monthly_turnover_aud': round(estimated_monthly_turnover, 2),
            'estimated_annual_turnover_aud': round(estimated_annual_turnover, 2),
            'sustainable_monthly_rent_aud': round(sustainable_monthly_rent, 2),
            'sustainable_annual_rent_aud': round(sustainable_annual_rent, 2),
            'rent_per_sqm_annual_aud': round(estimated_rent_per_sqm_annual, 2),
            'commercial_arbitrage_tier': arbitrage_tier
        })

    df_out = pd.DataFrame(results)
    df_out = df_out.sort_values(by='estimated_annual_turnover_aud', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_out.to_csv(OUTPUT_MONETIZATION_CSV, index=False)
    print(f"Catchment monetization estimates saved to: {OUTPUT_MONETIZATION_CSV}")

    # Summary JSON
    total_network_annual_turnover = df_out['estimated_annual_turnover_aud'].sum()
    avg_annual_turnover = df_out['estimated_annual_turnover_aud'].mean()
    avg_rent_sqm = df_out['rent_per_sqm_annual_aud'].mean()

    summary = {
        "analysis_name": "GeoPulse Catchment Commercial Monetization & Revenue Potential",
        "total_locations_modeled": len(df_out),
        "total_estimated_network_annual_turnover_aud": round(float(total_network_annual_turnover), 2),
        "mean_annual_turnover_per_site_aud": round(float(avg_annual_turnover), 2),
        "mean_sustainable_rent_per_sqm_aud": round(float(avg_rent_sqm), 2),
        "top_5_revenue_generating_catchments": df_out.head(5)[[
            'sensor_name', 'precinct_name', 'recommended_tenant',
            'store_viability_index', 'estimated_annual_turnover_aud', 'sustainable_annual_rent_aud'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Monetization summary JSON saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- TOP 3 REVENUE POTENTIAL CATCHMENTS (AUD) ---")
    for site in summary['top_5_revenue_generating_catchments'][:3]:
        print(f"• {site['sensor_name']} ({site['precinct_name']}) - Annual GMV: ${site['estimated_annual_turnover_aud']:,.2f} | Rent Cap: ${site['sustainable_annual_rent_aud']:,.2f}")

    return df_out

if __name__ == '__main__':
    estimate_catchment_monetization()
