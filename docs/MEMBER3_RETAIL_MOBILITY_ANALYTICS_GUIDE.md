# Member 3: Spatial Mobility & Retail Catchment Analytics Guide
**Project**: GeoPulse: Hyper-Local Retail Mobility Analytics  
**Intern**: Amit Prajapati (GitHub: `amit20055` | Email: `amitprajapati0458@gmail.com`)  
**Designated Role**: Member 3 — Spatial Mobility & Retail Catchment Analyst  
**Organization**: Infotact Solutions (Batch-22.1 | Ref: ITS/DA/1838)  
**Branch**: `Amit-Prajapati`  

---

## 1. Executive Role Overview & Scope

As **Member 3 (Spatial Mobility & Retail Catchment Analyst)** on Project 2 (*GeoPulse*), my core responsibilities encompass transforming raw urban sensor telemetry into actionable commercial intelligence for corporate retail site selection, store cannibalization avoidance, spatial autocorrelation clustering, anomaly surge mining, commercial rent benchmarking, corridor velocity profiling, non-cannibalizing store portfolio expansion, and precinct pricing power benchmarking.

### Core Objectives:
1. **Spatial Precinct Clustering**: Geo-reference 91 Melbourne CBD pedestrian sensors, calculate proximity metrics to the commercial core, and cluster sensors into distinct commercial retail precincts.
2. **Temporal Footfall Dynamics**: Model 24-hour diurnal curves, identify morning/evening peak rush hours, and compute weekend surge elasticity ratios ($E_w$).
3. **Store Viability Index (SVI)**: Formulate and implement a multi-factor scoring model that quantifies commercial retail suitability on a 0–100 scale.
4. **Pedestrian Isochrone & Spatial Gravity Catchment Modeling**: Model 300m, 600m, and 1000m pedestrian walking buffers with spatial gravity decay to estimate true footfall capture pools.
5. **Store Cannibalization & Co-Location Risk Engine**: Formulate the Cannibalization Risk Index (CRI) between proximate sensors ($d \le 350\text{m}$) to prevent revenue dilution among sister franchises.
6. **Interactive Geospatial Dashboard**: Provide an interactive Leaflet/CartoDB web map (`geopulse_interactive_catchment_map.html`) with precinct overlays, SVI tier coloring, isochrone buffers, and cannibalization conflict lines.
7. **Retail Tenant Allocation Matrix**: Match site micro-profiles with 5 retail tenant archetypes (*Luxury Flagship, QSR Express, Experiential Dining, Convenience/Pharmacy, Boutique Pop-Up*).
8. **Catchment Monetization & Turnover Mechanics**: Estimate annual gross merchandise value (GMV) and maximum sustainable rent per square meter based on footfall conversion funnels.
9. **Multi-Scenario Sensitivity & Shock Resilience Modeling**: Stress test all catchments against adverse weather, holiday retail surges, and transit disruptions to evaluate asset defensibility.
10. **Spatial Autocorrelation & Local Moran's I (LISA)**: Detect spatial agglomeration, high-high hotspots, and spatial outliers across the Melbourne CBD pedestrian grid.
11. **Dynamic Footfall Anomaly & Surge Mining**: Identify event-driven traffic spikes (festivals, game days) and severe operational deficits via standardized Z-scores.
12. **Master Retail Site Selection Scorecard**: Deliver a corporate real estate scorecard linking SVI, LISA, CRI, GMV, and shock resilience into executive site investment decisions.
13. **Huff Gravity Model & Precinct Market Share Simulation**: Probabilistic retail patronage gravity modeling based on distance friction and precinct commercial mass.
14. **Day-to-Night Mobility & 24/7 Activation Profiler**: Classify daytime office hubs vs. late-night vitality entertainment corridors.
15. **Corridor Pedestrian Velocity & Dwell Potential**: Discriminate high-speed transit thoroughfares from experiential browsing promenades.
16. **Store Expansion Optimizer**: Algorithmic greedy facility location solver planning non-cannibalizing multi-store rollout portfolios.
17. **Dynamic Retail Rent Sensitivity & Break-Even Footfall**: Model Occupancy Cost Ratios (OCR) under footfall stress ($\pm 30\%$) and recommend fixed vs. hybrid percentage lease structures.
18. **Precinct Comparative Benchmarking & Landlord Pricing Power Index (PPI)**: Multi-criteria cross-precinct benchmarking ranking landlord leverage and tenant negotiation strength.

---

## 2. System Architecture & Modular Pipeline

The analytical framework developed in branch `Amit-Prajapati` is organized as follows:

```
GeoPulse/
├── data/
│   └── processed/
│       ├── geopulse.db                       # SQLite analytical warehouse (indexed)
│       └── pedestrian_mobility_sample.csv    # 50K row sample for rapid profiling
├── docs/
│   └── MEMBER3_RETAIL_MOBILITY_ANALYTICS_GUIDE.md # Technical documentation
├── reports/
│   ├── data_ingestion_summary.json           # Ingestion audit and table schemas
│   ├── sensor_spatial_profile.csv            # 91 sensors with precinct & CBD distance
│   ├── retail_precinct_summary.json          # Precinct footfall volume & density tiers
│   ├── hourly_diurnal_curves.csv             # 24-hour citywide diurnal profile
│   ├── sensor_weekend_elasticity.csv         # Per-sensor weekend surge ratio
│   ├── temporal_patterns_summary.json        # Peak hours and daypart volume shares
│   ├── store_viability_rankings.csv          # Ranked retail catchments with SVI scores
│   ├── store_viability_summary.json          # SVI distribution and tier breakdown
│   ├── pedestrian_catchment_radii.csv        # 300m/600m/1000m isochrone capture pools
│   ├── catchment_gravity_metrics.json        # Gravity accessibility index summary
│   ├── store_cannibalization_risk.csv        # Pairwise sensor overlap and CRI scores
│   ├── cannibalization_summary.json          # High-risk cannibalization corridors
│   ├── geopulse_interactive_catchment_map.html # Interactive Leaflet geospatial map
│   ├── tenant_site_recommendations.csv       # Recommended tenant format per sensor
│   ├── tenant_allocation_matrix.json         # Category allocation breakdown
│   ├── catchment_monetization_estimates.csv  # GMV and sustainable rent benchmarks
│   ├── monetization_summary.json             # Commercial turnover summaries
│   ├── catchment_scenario_simulation.csv     # Weather, holiday & transit stress test
│   ├── scenario_stress_test_summary.json     # Catchment resilience score (RSI) breakdown
│   ├── spatial_autocorrelation_lisa.csv      # Local Moran's I and LISA cluster tiers
│   ├── morans_i_summary.json                 # Global Moran's I spatial dependency summary
│   ├── footfall_anomalies_detected.csv       # Z-score event surges and deficits
│   ├── anomaly_detection_summary.json        # Historical event anomaly summary
│   ├── master_retail_site_scorecard.csv      # Executive site scorecard & investment matrix
│   ├── scorecard_summary.json                # Final site recommendation distribution
│   ├── huff_market_share_probabilities.csv   # Huff gravity retail patronage probabilities
│   ├── huff_model_summary.json               # Simulated precinct trade market share
│   ├── day_night_mobility_profiles.csv       # 24/7 activation archetypes and dayparts
│   ├── day_night_summary.json                # Day-to-night ratio (DNR) breakdown
│   ├── corridor_pedestrian_velocity.csv      # Dwell Potential Index & street velocity
│   ├── corridor_flow_summary.json            # Major arterial flow metrics
│   ├── store_expansion_portfolios.csv        # Optimal 3/5/8 store rollout candidate sets
│   ├── expansion_optimizer_summary.json      # Non-cannibalizing expansion plans
│   ├── rent_sensitivity_simulation.csv       # Break-even footfall & OCR stress ratios
│   ├── rent_elasticity_summary.json          # Fixed vs hybrid percentage lease breakdown
│   ├── precinct_comparative_benchmark.csv    # Cross-precinct ranking & PPI scores
│   ├── precinct_benchmark_summary.json       # Macro commercial market tiers
│   ├── MEMBER3_EXECUTIVE_CATCHMENT_REPORT.md # Executive Markdown dossier
│   └── executive_metrics_manifest.json       # Pipeline artifacts manifest
├── src/
│   ├── ingest_mobility_data.py               # Chunked ingestion pipeline (418 MB CSV -> SQLite)
│   ├── spatial_clustering.py                 # Haversine distance & precinct clustering
│   ├── temporal_mobility.py                  # Diurnal curves & weekend elasticity engine
│   ├── store_viability_index.py              # Multi-factor SVI scoring algorithm
│   ├── catchment_isochrone.py                # Pedestrian isochrones & spatial gravity model
│   ├── cannibalization_risk.py               # Pairwise cannibalization risk engine (CRI)
│   ├── generate_interactive_map.py           # Standalone interactive Leaflet web map
│   ├── tenant_site_recommender.py            # Retail tenant archetype matching engine
│   ├── catchment_monetization.py             # Sales turnover & sustainable rent model
│   ├── scenario_simulator.py                 # Multi-scenario stress test & resilience engine
│   ├── spatial_autocorrelation.py            # Global & Local Moran's I spatial dependency
│   ├── anomaly_detection.py                  # Z-score temporal surge & deficit miner
│   ├── retail_site_scorecard.py              # Master corporate site selection scorecard
│   ├── huff_gravity_model.py                 # Huff gravity trade area patronage engine
│   ├── day_night_activation.py               # Daypart & late-night vitality profiler
│   ├── corridor_velocity_analysis.py         # Street corridor flow velocity & dwell index
│   ├── store_expansion_optimizer.py          # Facility location expansion solver
│   ├── rent_sensitivity_model.py             # Occupancy cost ratio & rent elasticity
│   ├── precinct_benchmark_engine.py          # Cross-precinct comparative benchmarking
│   └── generate_executive_report.py          # Executive dossier & manifest compiler
└── tests/
    └── test_mobility_analytics.py            # Automated unit test suite (19/19 tests pass)
```

---

## 3. Mathematical Models & Pricing Power

### 3.1 Landlord Pricing Power Index (PPI)
$$\text{PPI} = 0.40 \cdot \overline{\text{SVI}} + 0.35 \cdot \min\left(100, \frac{\overline{\text{Rent}}_{/m^2}}{2500} \cdot 100\right) + 0.25 \cdot \overline{\text{RSI}}$$
* **Premium Landlord Markets (PPI $\ge 75$)**: Southbank Waterfront (80.67) and Central Retail Core (80.43).
* **Balanced Commercial Markets (PPI 60–74.9)**: Flinders Transit Hub (71.74) and Chinatown Dining (71.03).
* **Tenant-Favorable Markets (PPI $< 60$)**: Docklands Harbourside (51.75) and Northern University Corridor (48.99).

### 3.2 Break-Even Footfall & Critical Lease Stress
$$\text{GMV}_{\min} = \frac{\text{Base Rent}}{0.18} \implies V_{\text{break-even}} = \bar{V} \cdot \left(\frac{\text{GMV}_{\min}}{\text{GMV}_{\text{base}}}\right)$$

---

## 4. Verification & Testing

To execute all unit test suites and verify 100% test pass rate:
```powershell
python -m unittest discover tests
```
*Result: 19/19 tests passed cleanly in 0.320s.*
