"""
GeoPulse Mobility Analytics - Comprehensive Unit Test Suite
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import unittest
import sqlite3
import pandas as pd
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "geopulse.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

class TestGeoPulseMobilityAnalytics(unittest.TestCase):

    def test_01_database_and_warehouse_integrity(self):
        """Verify SQLite analytical database contains valid sensor and mobility tables."""
        self.assertTrue(os.path.exists(DB_PATH), f"Database not found at {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn("sensor_locations", tables)
        self.assertIn("hourly_pedestrian_counts", tables)

        cursor.execute("SELECT COUNT(*) FROM sensor_locations;")
        sensor_count = cursor.fetchone()[0]
        self.assertGreaterEqual(sensor_count, 50, "Sensor table should have at least 50 sensors")

        cursor.execute("SELECT COUNT(*) FROM hourly_pedestrian_counts;")
        records_count = cursor.fetchone()[0]
        self.assertGreaterEqual(records_count, 100000, "Hourly counts table should have ingested records")

        conn.close()

    def test_02_spatial_clustering_profile(self):
        """Verify retail precinct clustering generates valid clusters and density tiers."""
        spatial_csv = os.path.join(REPORTS_DIR, "sensor_spatial_profile.csv")
        self.assertTrue(os.path.exists(spatial_csv), "sensor_spatial_profile.csv must exist")

        df = pd.read_csv(spatial_csv)
        self.assertIn("sensor_id", df.columns)
        self.assertIn("retail_precinct", df.columns)
        self.assertIn("density_tier", df.columns)
        self.assertIn("distance_to_cbd_center_m", df.columns)

        self.assertEqual(df['retail_precinct'].isnull().sum(), 0)
        self.assertGreaterEqual(df['retail_precinct'].nunique(), 4)

    def test_03_temporal_mobility_curves(self):
        """Verify 24-hour diurnal curves and weekend elasticity metrics."""
        diurnal_csv = os.path.join(REPORTS_DIR, "hourly_diurnal_curves.csv")
        elasticity_csv = os.path.join(REPORTS_DIR, "sensor_weekend_elasticity.csv")

        self.assertTrue(os.path.exists(diurnal_csv), "hourly_diurnal_curves.csv must exist")
        self.assertTrue(os.path.exists(elasticity_csv), "sensor_weekend_elasticity.csv must exist")

        df_diurnal = pd.read_csv(diurnal_csv)
        self.assertEqual(len(df_diurnal), 24)
        self.assertIn("mean_footfall", df_diurnal.columns)
        self.assertIn("total_volume", df_diurnal.columns)

        df_elasticity = pd.read_csv(elasticity_csv)
        self.assertIn("weekend_ratio", df_elasticity.columns)
        self.assertIn("retail_mobility_classification", df_elasticity.columns)
        self.assertTrue((df_elasticity['weekend_ratio'] > 0).all())

    def test_04_store_viability_index_metrics(self):
        """Verify SVI algorithm produces valid 0-100 scores and consistent ranking."""
        svi_csv = os.path.join(REPORTS_DIR, "store_viability_rankings.csv")
        summary_json = os.path.join(REPORTS_DIR, "store_viability_summary.json")

        self.assertTrue(os.path.exists(svi_csv), "store_viability_rankings.csv must exist")
        self.assertTrue(os.path.exists(summary_json), "store_viability_summary.json must exist")

        df_svi = pd.read_csv(svi_csv)
        self.assertIn("store_viability_index", df_svi.columns)
        self.assertIn("viability_tier", df_svi.columns)
        self.assertIn("rank", df_svi.columns)

        self.assertTrue((df_svi['store_viability_index'] >= 0).all())
        self.assertTrue((df_svi['store_viability_index'] <= 100).all())

        for sub_col in ['score_volume', 'score_stability', 'score_weekend_surge', 'score_precinct_synergy']:
            self.assertTrue((df_svi[sub_col] >= 0).all(), f"{sub_col} has negative values")
            self.assertTrue((df_svi[sub_col] <= 100).all(), f"{sub_col} exceeds 100")

        self.assertEqual(df_svi['rank'].min(), 1)

    def test_05_pedestrian_catchment_isochrones(self):
        """Verify pedestrian isochrone radii and spatial gravity calculation."""
        catchment_csv = os.path.join(REPORTS_DIR, "pedestrian_catchment_radii.csv")
        gravity_json = os.path.join(REPORTS_DIR, "catchment_gravity_metrics.json")

        self.assertTrue(os.path.exists(catchment_csv), "pedestrian_catchment_radii.csv must exist")
        self.assertTrue(os.path.exists(gravity_json), "catchment_gravity_metrics.json must exist")

        df_catchment = pd.read_csv(catchment_csv)
        self.assertIn("effective_capture_potential", df_catchment.columns)
        self.assertIn("spatial_gravity_accessibility", df_catchment.columns)
        self.assertTrue((df_catchment['effective_capture_potential'] >= 0).all())

    def test_06_store_cannibalization_risk(self):
        """Verify store cannibalization indices and pairwise separation distance."""
        cannibal_csv = os.path.join(REPORTS_DIR, "store_cannibalization_risk.csv")
        summary_json = os.path.join(REPORTS_DIR, "cannibalization_summary.json")

        self.assertTrue(os.path.exists(cannibal_csv), "store_cannibalization_risk.csv must exist")
        self.assertTrue(os.path.exists(summary_json), "cannibalization_summary.json must exist")

        df_cannibal = pd.read_csv(cannibal_csv)
        self.assertIn("cannibalization_risk_index", df_cannibal.columns)
        self.assertIn("distance_meters", df_cannibal.columns)
        self.assertTrue((df_cannibal['cannibalization_risk_index'] >= 0).all())
        self.assertTrue((df_cannibal['cannibalization_risk_index'] <= 100).all())

    def test_07_interactive_map_and_tenant_recommendations(self):
        """Verify HTML map existence and tenant recommendation allocations."""
        map_html = os.path.join(REPORTS_DIR, "geopulse_interactive_catchment_map.html")
        rec_csv = os.path.join(REPORTS_DIR, "tenant_site_recommendations.csv")

        self.assertTrue(os.path.exists(map_html), "geopulse_interactive_catchment_map.html must exist")
        self.assertGreater(os.path.getsize(map_html), 10000, "Map HTML must be populated")

        self.assertTrue(os.path.exists(rec_csv), "tenant_site_recommendations.csv must exist")
        df_rec = pd.read_csv(rec_csv)
        self.assertIn("primary_recommended_tenant", df_rec.columns)
        self.assertIn("strategic_rationale", df_rec.columns)
        self.assertEqual(df_rec['primary_recommended_tenant'].isnull().sum(), 0)

if __name__ == '__main__':
    unittest.main()
