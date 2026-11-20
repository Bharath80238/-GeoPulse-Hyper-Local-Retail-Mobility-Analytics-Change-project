"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Store Viability Index (SVI) & Catchment Scoring Engine
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "geopulse.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SPATIAL_CSV = os.path.join(REPORTS_DIR, "sensor_spatial_profile.csv")
ELASTICITY_CSV = os.path.join(REPORTS_DIR, "sensor_weekend_elasticity.csv")
OUTPUT_RANKINGS_CSV = os.path.join(REPORTS_DIR, "store_viability_rankings.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "store_viability_summary.json")

def min_max_scale(series, invert=False):
    """Normalize a series to 0-100 scale."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(50.0, index=series.index)
    if invert:
        scaled = 100.0 * (max_val - series) / (max_val - min_val)
    else:
        scaled = 100.0 * (series - min_val) / (max_val - min_val)
    return scaled.clip(0, 100)

def compute_store_viability_index():
    print("=" * 70)
    print("GeoPulse: Computing Store Viability Index (SVI) & Retail Catchment Rankings")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run ingest_mobility_data.py first.")

    conn = sqlite3.connect(DB_PATH)

    # 1. Footfall volume & traffic stability per sensor
    print("1. Extracting traffic distribution and stability per sensor from analytical warehouse...")
    query = """
    SELECT 
        sensor_id,
        sensor_name,
        COUNT(*) as total_hours,
        SUM(hourly_counts) as total_volume,
        AVG(hourly_counts) as avg_hourly_footfall,
        MAX(hourly_counts) as peak_single_hour,
        AVG(hourly_counts * hourly_counts) - (AVG(hourly_counts) * AVG(hourly_counts)) as variance_counts
    FROM hourly_pedestrian_counts
    GROUP BY sensor_id, sensor_name
    """
    df_vol = pd.read_sql_query(query, conn)
    conn.close()

    # Calculate standard deviation and coefficient of variation (CV = std / mean)
    df_vol['std_hourly_footfall'] = np.sqrt(np.maximum(df_vol['variance_counts'], 0))
    df_vol['coefficient_of_variation'] = df_vol['std_hourly_footfall'] / df_vol['avg_hourly_footfall'].replace(0, np.nan)
    df_vol['coefficient_of_variation'] = df_vol['coefficient_of_variation'].fillna(1.0)

    # 2. Integrate Spatial Precinct and Weekend Elasticity data
    print("2. Integrating spatial precinct profiling and weekend elasticity...")
    if os.path.exists(SPATIAL_CSV):
        df_spatial = pd.read_csv(SPATIAL_CSV)[['sensor_id', 'latitude', 'longitude', 'retail_precinct', 'density_tier']]
        df_spatial = df_spatial.rename(columns={'retail_precinct': 'precinct_name'})
    else:
        df_spatial = pd.DataFrame(columns=['sensor_id', 'latitude', 'longitude', 'precinct_name', 'density_tier'])

    if os.path.exists(ELASTICITY_CSV):
        df_elasticity = pd.read_csv(ELASTICITY_CSV)[['sensor_id', 'weekend_ratio', 'retail_mobility_classification']]
        df_elasticity = df_elasticity.rename(columns={
            'weekend_ratio': 'weekend_surge_ratio',
            'retail_mobility_classification': 'behavior_profile'
        })
    else:
        df_elasticity = pd.DataFrame(columns=['sensor_id', 'weekend_surge_ratio', 'behavior_profile'])

    # Merge features
    df = df_vol.merge(df_spatial, on='sensor_id', how='left')
    df = df.merge(df_elasticity, on='sensor_id', how='left')

    # Fill missing values if any
    df['weekend_surge_ratio'] = df['weekend_surge_ratio'].fillna(1.0)
    df['precinct_name'] = df['precinct_name'].fillna('General Urban Core')

    # Calculate Precinct Synergy: Aggregate average volume per precinct
    precinct_avg = df.groupby('precinct_name')['avg_hourly_footfall'].transform('mean')
    df['precinct_synergy_raw'] = precinct_avg

    # 3. Component Scoring (0-100 scale)
    print("3. Calculating normalized sub-scores...")
    # Volume Score (35% weight)
    df['score_volume'] = min_max_scale(np.log1p(df['avg_hourly_footfall'])).round(2)

    # Stability Score (25% weight) - Lower CV means higher stability
    df['score_stability'] = min_max_scale(df['coefficient_of_variation'], invert=True).round(2)

    # Weekend Surge Score (20% weight) - Balanced elasticity around 1.0
    # Sensors that sustain high weekend traffic or experience balanced retail trade
    df['score_weekend_surge'] = min_max_scale(df['weekend_surge_ratio']).round(2)

    # Precinct Synergy Score (20% weight)
    df['score_precinct_synergy'] = min_max_scale(np.log1p(df['precinct_synergy_raw'])).round(2)

    # 4. Composite Store Viability Index (SVI)
    print("4. Computing composite Store Viability Index (SVI)...")
    # SVI Formula: 35% Volume + 25% Stability + 20% Surge + 20% Synergy
    df['store_viability_index'] = (
        0.35 * df['score_volume'] +
        0.25 * df['score_stability'] +
        0.20 * df['score_weekend_surge'] +
        0.20 * df['score_precinct_synergy']
    ).round(2)

    # Tier Classification
    def classify_viability_tier(svi):
        if svi >= 80.0:
            return "Tier 1 - Flagship Catchment"
        elif svi >= 65.0:
            return "Tier 2 - High-Yield Commercial Hub"
        elif svi >= 50.0:
            return "Tier 3 - Moderate Local Catchment"
        else:
            return "Tier 4 - Peripheral / Low-Footfall"

    df['viability_tier'] = df['store_viability_index'].apply(classify_viability_tier)

    # Ranking
    df['rank'] = df['store_viability_index'].rank(ascending=False, method='dense').astype(int)
    df = df.sort_values(by=['store_viability_index', 'total_volume'], ascending=[False, False])

    # Select columns for clean export
    export_cols = [
        'rank',
        'sensor_id',
        'sensor_name',
        'precinct_name',
        'store_viability_index',
        'viability_tier',
        'score_volume',
        'score_stability',
        'score_weekend_surge',
        'score_precinct_synergy',
        'avg_hourly_footfall',
        'peak_single_hour',
        'weekend_surge_ratio',
        'behavior_profile',
        'latitude',
        'longitude'
    ]
    df_export = df[export_cols]

    # Save to CSV
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_export.to_csv(OUTPUT_RANKINGS_CSV, index=False)
    print(f"Store Viability rankings saved to: {OUTPUT_RANKINGS_CSV}")

    # Summary Statistics
    tier_counts = df['viability_tier'].value_counts().to_dict()
    precinct_rankings = df.groupby('precinct_name')['store_viability_index'].mean().round(2).sort_values(ascending=False).to_dict()

    top_10 = df_export.head(10)[[
        'rank', 'sensor_name', 'precinct_name', 'store_viability_index', 'viability_tier'
    ]].to_dict(orient='records')

    summary = {
        "total_sensors_analyzed": len(df),
        "mean_store_viability_index": round(float(df['store_viability_index'].mean()), 2),
        "median_store_viability_index": round(float(df['store_viability_index'].median()), 2),
        "max_store_viability_index": round(float(df['store_viability_index'].max()), 2),
        "min_store_viability_index": round(float(df['store_viability_index'].min()), 2),
        "tier_distribution": tier_counts,
        "precinct_average_viability": precinct_rankings,
        "top_10_retail_catchments": top_10
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Store Viability summary JSON saved to: {OUTPUT_SUMMARY_JSON}")

    print("\n--- TOP 5 RETAIL CATCHMENTS BY SVI ---")
    for row in top_10[:5]:
        print(f"Rank {row['rank']}: {row['sensor_name']} ({row['precinct_name']}) - SVI: {row['store_viability_index']} [{row['viability_tier']}]")

    print("\n--- VIABILITY TIER DISTRIBUTION ---")
    for tier, count in tier_counts.items():
        print(f"  * {tier}: {count} locations ({count/len(df)*100:.1f}%)")

    return df_export

if __name__ == "__main__":
    compute_store_viability_index()
