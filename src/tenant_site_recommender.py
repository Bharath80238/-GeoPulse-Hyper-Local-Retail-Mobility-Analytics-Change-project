"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Retail Tenant Recommendation Engine
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SVI_CSV = os.path.join(REPORTS_DIR, "store_viability_rankings.csv")
OUTPUT_RECOMMENDATIONS_CSV = os.path.join(REPORTS_DIR, "tenant_site_recommendations.csv")
OUTPUT_MATRIX_JSON = os.path.join(REPORTS_DIR, "tenant_allocation_matrix.json")

def recommend_tenant_formats():
    print("=" * 70)
    print("GeoPulse: Computing Retail Tenant Site Matching & Allocation Matrix")
    print("=" * 70)

    if not os.path.exists(SVI_CSV):
        raise FileNotFoundError(f"Missing {SVI_CSV}. Run store_viability_index.py first.")

    df = pd.read_csv(SVI_CSV)

    recommendations = []

    for _, row in df.iterrows():
        svi = row['store_viability_index']
        vol = row['avg_hourly_footfall']
        ratio = row['weekend_surge_ratio']
        stability = row['score_stability']
        precinct = row['precinct_name']
        sensor_name = row['sensor_name']
        sensor_id = row['sensor_id']

        # Tenant Matching Logic based on Mobility Physics
        matched_tenants = []
        primary_fit = ""
        reasoning = ""

        # 1. Luxury / Flagship Retail
        if svi >= 75.0 and "Central Retail Core" in precinct:
            matched_tenants.append("Luxury & International Flagship")
            primary_fit = "Luxury / Flagship Brand"
            reasoning = "Exceptional pedestrian gravity, high precinct synergy, and high footfall density."

        # 2. QSR / Coffee Express (Commuter corridors)
        elif ratio <= 0.88 and vol >= 400.0:
            matched_tenants.append("QSR & Express Coffee")
            primary_fit = "QSR / Grab-and-Go"
            reasoning = "Heavy weekday commuter flows with high peak turnover; ideal for quick-service F&B."

        # 3. Experiential Dining & Nightlife (Weekend surge)
        elif ratio >= 1.15 and ("Southbank" in precinct or "Chinatown" in precinct or vol >= 300.0):
            matched_tenants.append("Experiential Dining & Evening Lounge")
            primary_fit = "Experiential Dining / Nightlife"
            reasoning = "Strong weekend leisure elasticity and high evening pedestrian density."

        # 4. Everyday Convenience & Pharmacy
        elif stability >= 55.0 and vol >= 250.0:
            matched_tenants.append("Everyday Convenience & Pharmacy")
            primary_fit = "Convenience Retail / Essential Services"
            reasoning = "Consistent, low-variance pedestrian flow suitable for daily essentials and pharmacy."

        # 5. Boutique / Pop-Up / Dark Kitchen
        else:
            matched_tenants.append("Artisan Boutique & Specialty Pop-Up")
            primary_fit = "Artisan Boutique / Specialty Retail"
            reasoning = "Niche catchment or peripheral street; suited for destination retail or low-capex pop-ups."

        recommendations.append({
            'sensor_id': sensor_id,
            'sensor_name': sensor_name,
            'precinct_name': precinct,
            'store_viability_index': svi,
            'avg_hourly_footfall': vol,
            'weekend_surge_ratio': ratio,
            'primary_recommended_tenant': primary_fit,
            'strategic_rationale': reasoning
        })

    df_rec = pd.DataFrame(recommendations)
    df_rec = df_rec.sort_values(by=['store_viability_index', 'avg_hourly_footfall'], ascending=[False, False])

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_rec.to_csv(OUTPUT_RECOMMENDATIONS_CSV, index=False)
    print(f"Tenant site recommendations saved to: {OUTPUT_RECOMMENDATIONS_CSV}")

    # Summary breakdown
    tenant_counts = df_rec['primary_recommended_tenant'].value_counts().to_dict()

    summary = {
        "analysis_name": "GeoPulse Retail Tenant Site Allocation Framework",
        "total_sites_analyzed": len(df_rec),
        "tenant_category_breakdown": tenant_counts,
        "sample_recommendations": df_rec.head(6)[[
            'sensor_name', 'precinct_name', 'store_viability_index', 'primary_recommended_tenant', 'strategic_rationale'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_MATRIX_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Tenant allocation matrix saved to: {OUTPUT_MATRIX_JSON}")

    print("\n--- TENANT CATEGORY ALLOCATION BREAKDOWN ---")
    for category, count in tenant_counts.items():
        print(f"  • {category}: {count} sites ({count/len(df_rec)*100:.1f}%)")

    return df_rec

if __name__ == '__main__':
    recommend_tenant_formats()
