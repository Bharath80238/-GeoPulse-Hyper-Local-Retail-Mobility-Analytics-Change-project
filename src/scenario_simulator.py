"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Multi-Scenario Pedestrian Stress Testing & Sensitivity Simulator
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
OUTPUT_SIMULATION_CSV = os.path.join(REPORTS_DIR, "catchment_scenario_simulation.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "scenario_stress_test_summary.json")

def simulate_catchment_scenarios():
    print("=" * 70)
    print("GeoPulse: Simulating Retail Catchment Sensitivity Under Urban Stress Scenarios")
    print("=" * 70)

    if not os.path.exists(SVI_CSV) or not os.path.exists(MONETIZATION_CSV):
        raise FileNotFoundError("Prerequisite CSV files missing. Run earlier pipelines first.")

    df_svi = pd.read_csv(SVI_CSV)
    df_mon = pd.read_csv(MONETIZATION_CSV)[['sensor_id', 'estimated_monthly_turnover_aud']]

    df = df_svi.merge(df_mon, on='sensor_id', how='left')

    simulation_rows = []

    for _, row in df.iterrows():
        base_vol = row['avg_hourly_footfall']
        base_gmv = row['estimated_monthly_turnover_aud']
        precinct = row['precinct_name']
        name = row['sensor_name']
        sid = row['sensor_id']

        # Determine physical location typology (enclosed/covered vs open-street)
        is_enclosed = any(term in name.lower() for term in ['central', 'arcade', 'underpass', 'concourse', 'station'])
        is_transit = "Transit" in precinct or any(term in name.lower() for term in ['station', 'flinders', 'southern'])

        # --- SCENARIO 1: Severe Weather / Torrential Rain ---
        # Enclosed/indoor catchments act as shelter (+20% to +30%), open streets drop (-35% to -50%)
        if is_enclosed:
            weather_delta_pct = 0.25
        else:
            weather_delta_pct = -0.38
        vol_weather = max(base_vol * (1.0 + weather_delta_pct), 5.0)
        gmv_weather = base_gmv * (1.0 + weather_delta_pct)

        # --- SCENARIO 2: Holiday Shopping Surge (Boxing Day / Black Friday) ---
        # Prime retail core surges dramatically (+80%), leisure dining (+45%), transit (+30%)
        if "Central Retail Core" in precinct:
            holiday_delta_pct = 0.85
        elif "Chinatown" in precinct or "Southbank" in precinct:
            holiday_delta_pct = 0.50
        else:
            holiday_delta_pct = 0.30
        vol_holiday = base_vol * (1.0 + holiday_delta_pct)
        gmv_holiday = base_gmv * (1.0 + holiday_delta_pct)

        # --- SCENARIO 3: Commuter Rail Disruption / Strike ---
        # Transit hubs drop severely (-65%), suburban/university fringes are resilient (-5%)
        if is_transit:
            transit_strike_delta_pct = -0.65
        elif "Central Retail Core" in precinct:
            transit_strike_delta_pct = -0.30
        else:
            transit_strike_delta_pct = -0.10
        vol_strike = max(base_vol * (1.0 + transit_strike_delta_pct), 5.0)
        gmv_strike = base_gmv * (1.0 + transit_strike_delta_pct)

        # Composite Resilience Score (RSI, 0-100 scale)
        # Higher score = lower downside deviation during adverse shocks
        downside_weather = abs(min(weather_delta_pct, 0.0))
        downside_strike = abs(min(transit_strike_delta_pct, 0.0))
        avg_downside_penalty = (downside_weather * 0.45) + (downside_strike * 0.55)
        resiliency_score = round(max(100.0 - (avg_downside_penalty * 100.0), 10.0), 2)

        if resiliency_score >= 75.0:
            resilience_tier = "High Shock Resilience (All-Weather Asset)"
        elif resiliency_score >= 55.0:
            resilience_tier = "Moderate Shock Resilience"
        else:
            resilience_tier = "Vulnerable to External Urban Shocks"

        simulation_rows.append({
            'sensor_id': sid,
            'sensor_name': name,
            'precinct_name': precinct,
            'baseline_hourly_footfall': round(base_vol, 1),
            'baseline_monthly_turnover_aud': round(base_gmv, 2),
            'weather_shock_footfall': round(vol_weather, 1),
            'weather_shock_delta_pct': round(weather_delta_pct * 100.0, 1),
            'weather_shock_turnover_aud': round(gmv_weather, 2),
            'holiday_surge_footfall': round(vol_holiday, 1),
            'holiday_surge_delta_pct': round(holiday_delta_pct * 100.0, 1),
            'holiday_surge_turnover_aud': round(gmv_holiday, 2),
            'transit_strike_footfall': round(vol_strike, 1),
            'transit_strike_delta_pct': round(transit_strike_delta_pct * 100.0, 1),
            'transit_strike_turnover_aud': round(gmv_strike, 2),
            'catchment_resilience_score': resiliency_score,
            'resilience_tier': resilience_tier
        })

    df_sim = pd.DataFrame(simulation_rows)
    df_sim = df_sim.sort_values(by='catchment_resilience_score', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_sim.to_csv(OUTPUT_SIMULATION_CSV, index=False)
    print(f"Scenario simulation results saved to: {OUTPUT_SIMULATION_CSV}")

    # Summary JSON
    summary = {
        "analysis_name": "GeoPulse Urban Stress & Sensitivity Simulator",
        "total_catchments_simulated": len(df_sim),
        "mean_catchment_resilience_score": round(float(df_sim['catchment_resilience_score'].mean()), 2),
        "resilience_tier_breakdown": df_sim['resilience_tier'].value_counts().to_dict(),
        "top_5_most_resilient_sites": df_sim.head(5)[[
            'sensor_name', 'precinct_name', 'catchment_resilience_score', 'resilience_tier'
        ]].to_dict(orient='records'),
        "top_5_most_vulnerable_sites": df_sim.tail(5)[[
            'sensor_name', 'precinct_name', 'catchment_resilience_score', 'resilience_tier'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Scenario stress test summary saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- TOP 3 ALL-WEATHER RESILIENT SITES ---")
    for site in summary['top_5_most_resilient_sites'][:3]:
        print(f"• {site['sensor_name']} ({site['precinct_name']}) - Resilience Score: {site['catchment_resilience_score']} [{site['resilience_tier']}]")

    print("\n--- TOP 3 MOST VULNERABLE SITES (HIGH TRANSIT / OPEN EXPOSURE) ---")
    for site in summary['top_5_most_vulnerable_sites'][:3]:
        print(f"• {site['sensor_name']} ({site['precinct_name']}) - Resilience Score: {site['catchment_resilience_score']} [{site['resilience_tier']}]")

    return df_sim

if __name__ == '__main__':
    simulate_catchment_scenarios()
