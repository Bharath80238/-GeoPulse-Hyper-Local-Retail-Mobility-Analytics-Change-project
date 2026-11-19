# Week 2 Mid-Term Technical Synthesis Report
**Project**: GeoPulse: Hyper-Local Retail Mobility Analytics  
**Intern**: Amit Prajapati (GitHub: `amit20055` | Email: `amitprajapati0458@gmail.com`)  
**Designated Role**: Member 3 — Spatial Mobility & Retail Catchment Analyst  
**Organization**: Infotact Solutions (Batch-22.1 | Ref: ITS/DA/1838)  
**Milestone Window**: 17 Nov 2026 – 24 Nov 2026  

---

## 1. Executive Summary & Review Scope

This technical report documents the comprehensive delivery of Member 3's core analytical modeling during Week 2 of the GeoPulse retail mobility project. Building upon the Week 1 spatial baseline and telemetry warehouse, Week 2 focused on multi-criteria catchment modeling, retail site selection viability, spatial gravity physics, and corporate lease benchmarking.

### Core Mathematical Models Implemented:
1. **Spatial Precinct Clustering**: Segmented 91 CBD sensors into 6 commercial zones using Haversine distance and density tiering.
2. **Store Viability Index (SVI)**: Multi-factor commercial retail index ($0–100$) weighting volume (35%), stability (25%), weekend surge (20%), and precinct synergy (20%).
3. **Pedestrian Isochrone & Spatial Gravity Model**: 300m, 600m, and 1000m walking buffers with distance decay ($A_i = \sum \frac{V_j}{d_{ij}^{1.5}}$).
4. **Store Cannibalization Risk Engine (CRI)**: Pairwise overlap detection within 350m to prevent sister franchise sales dilution.
5. **Interactive Geospatial Dashboard**: Interactive Leaflet/CartoDB web application (`geopulse_interactive_catchment_map.html`).
6. **Leisure Gravity & Experiential Vitality**: Modeled dining and weekend vitality ratios across Southbank and Chinatown.
7. **Storefront Visual Exposure Index**: Formulated corner placement and bidirectional exposure multipliers.
8. **Transit Modal Split**: Quantified heavy rail versus light rail pedestrian feeder gravity.

---

## 2. Milestone Deliverables Summary

| Module Script | Key Output Report | Focus Area |
|:---|:---|:---|
| `src/store_viability_index.py` | `reports/store_viability_rankings.csv` | Proprietary SVI 0-100 site scoring |
| `src/catchment_isochrone.py` | `reports/pedestrian_catchment_radii.csv` | 300m/600m/1000m walking isochrones |
| `src/cannibalization_risk.py` | `reports/store_cannibalization_risk.csv` | Cannibalization Risk Index (CRI) |
| `src/generate_interactive_map.py` | `reports/geopulse_interactive_catchment_map.html` | Interactive geospatial visualization |
| `src/leisure_gravity_scoring.py` | `reports/leisure_gravity_rankings.csv` | Weekend dining & evening vitality |
| `src/storefront_visibility_index.py` | `reports/storefront_visibility_ratings.csv` | Visual exposure and corner grading |
| `src/transit_catchment_modal_split.py` | `reports/transit_catchment_modal_split.csv` | Transit hub feeder modal split |

---

## 3. Test Suite & Validation
All Week 2 pipelines are covered by automated unit tests (`tests/test_mobility_analytics.py`) with 100% test pass rate.
