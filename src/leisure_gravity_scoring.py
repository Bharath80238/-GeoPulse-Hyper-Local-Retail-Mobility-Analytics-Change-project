"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Leisure Gravity & Experiential Dining Catchment Scoring
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
OUTPUT_LEISURE_CSV = os.path.join(REPORTS_DIR, "leisure_gravity_rankings.csv")
OUTPUT_SUMMARY_JSON = os.path.join(REPORTS_DIR, "leisure_gravity_summary.json")

def score_leisure_gravity():
    print("=" * 70)
    print("GeoPulse: Computing Weekend Leisure Gravity & Experiential Vitality")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database missing at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        s.sensor_id,
        s.sensor_name,
        COALESCE(s.sensor_description, s.sensor_name) as sensor_desc,
        AVG(CASE WHEN h.day IN ('Saturday', 'Sunday') THEN h.hourly_counts ELSE NULL END) as weekend_avg,
        AVG(CASE WHEN h.day NOT IN ('Saturday', 'Sunday') THEN h.hourly_counts ELSE NULL END) as weekday_avg,
        AVG(CASE WHEN h.time BETWEEN 18 AND 23 THEN h.hourly_counts ELSE NULL END) as evening_avg
    FROM sensor_locations s
    JOIN hourly_pedestrian_counts h ON s.sensor_id = h.sensor_id
    GROUP BY s.sensor_id, s.sensor_name, s.sensor_description
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['weekend_avg'] = df['weekend_avg'].fillna(100.0)
    df['weekday_avg'] = df['weekday_avg'].fillna(100.0)
    df['evening_avg'] = df['evening_avg'].fillna(50.0)

    # Leisure Gravity Index (LGI): combines weekend ratio, evening volume, and raw weekend volume
    df['weekend_elasticity'] = (df['weekend_avg'] / df['weekday_avg']).round(2)

    # LGI = 0.40 * norm(log(weekend_avg)) + 0.35 * norm(log(evening_avg)) + 0.25 * norm(weekend_elasticity)
    def scale_0_100(s):
        s_min, s_max = s.min(), s.max()
        return 100.0 * (s - s_min) / (s_max - s_min) if s_max > s_min else pd.Series(50.0, index=s.index)

    score_vol = scale_0_100(np.log1p(df['weekend_avg']))
    score_eve = scale_0_100(np.log1p(df['evening_avg']))
    score_ela = scale_0_100(df['weekend_elasticity'])

    df['leisure_gravity_index'] = (0.40 * score_vol + 0.35 * score_eve + 0.25 * score_ela).round(2)

    def classify_leisure_tier(lgi):
        if lgi >= 75.0:
            return "Premier Experiential / Nightlife Anchor"
        elif lgi >= 55.0:
            return "High Leisure Dining Corridor"
        elif lgi >= 40.0:
            return "Balanced Community Strip"
        else:
            return "Low Leisure Vitality (Office / Commuter Dominated)"

    df['leisure_tier'] = df['leisure_gravity_index'].apply(classify_leisure_tier)
    df_out = df.sort_values(by='leisure_gravity_index', ascending=False)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_out.to_csv(OUTPUT_LEISURE_CSV, index=False)
    print(f"Leisure gravity rankings saved to: {OUTPUT_LEISURE_CSV}")

    summary = {
        "analysis_name": "GeoPulse Leisure Gravity & Experiential Vitality",
        "total_sensors": len(df_out),
        "mean_leisure_gravity_index": round(float(df_out['leisure_gravity_index'].mean()), 2),
        "leisure_tier_distribution": df_out['leisure_tier'].value_counts().to_dict(),
        "top_leisure_destinations": df_out.head(5)[[
            'sensor_desc', 'weekend_avg', 'weekend_elasticity', 'leisure_gravity_index', 'leisure_tier'
        ]].to_dict(orient='records')
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Leisure summary saved to: {OUTPUT_SUMMARY_JSON}")

    return df_out

if __name__ == '__main__':
    score_leisure_gravity()
