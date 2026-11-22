# Member 3: Spatial Mobility & Retail Catchment Analytics Guide
**Project**: GeoPulse: Hyper-Local Retail Mobility Analytics  
**Intern**: Amit Prajapati (GitHub: `amit20055` | Email: `amitprajapati0458@gmail.com`)  
**Designated Role**: Member 3 — Spatial Mobility & Retail Catchment Analyst  
**Organization**: Infotact Solutions (Batch-22.1 | Ref: ITS/DA/1838)  
**Branch**: `Amit-Prajapati`  

---

## 1. Executive Role Overview & Scope

As **Member 3 (Spatial Mobility & Retail Catchment Analyst)** on Project 2 (*GeoPulse*), my core responsibilities encompass transforming raw urban sensor telemetry into actionable commercial intelligence for corporate retail site selection, store cannibalization avoidance, pedestrian trade area modeling, commercial rent benchmarking, and urban stress scenario testing.

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
10. **Automated Executive Dossier Compilation**: Systematically generate high-level executive reports and pipeline manifests.

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
│   └── generate_executive_report.py          # Executive dossier & manifest compiler
└── tests/
    └── test_mobility_analytics.py            # Automated unit test suite (10/10 tests pass)
```

---

## 3. Mathematical Models & Equations

### 3.1 Proximity Calculation (Haversine Formula)
Distance $d$ in meters between sensor $(\phi_1, \lambda_1)$ and Melbourne CBD centroid $(\phi_0, \lambda_0) = (-37.8136, 144.9631)$:
$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_0)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$
$$d = 2 R \cdot \arcsin\left(\sqrt{a}\right) \quad \text{where } R = 6,371,000 \text{ m}$$

### 3.2 Weekend Surge Elasticity Ratio ($E_w$)
Measures whether a catchment is commuter-dominated ($E_w < 0.75$), balanced ($0.75 \le E_w \le 1.25$), or leisure-driven ($E_w > 1.25$):
$$E_w = \frac{\bar{V}_{\text{weekend}}}{\bar{V}_{\text{weekday}}}$$

### 3.3 Store Viability Index (SVI)
$$\text{SVI} = 0.35 \cdot S_{\text{vol}} + 0.25 \cdot S_{\text{stab}} + 0.20 \cdot S_{\text{surge}} + 0.20 \cdot S_{\text{precinct}}$$

### 3.4 Spatial Gravity & Catchment Accessibility Index
$$A_i = \sum_{j \neq i} \frac{V_j}{d_{ij}^\beta} \quad (\beta = 1.5)$$

### 3.5 Cannibalization Risk Index (CRI)
$$\text{CRI}_{ij} = 100 \times \left( \frac{\min(V_i, V_j)}{\max(V_i, V_j)} \right)^{0.5} \times \exp\left(-\frac{d_{ij}}{200}\right)$$

### 3.6 Commercial Turnover & Sustainable Rent Benchmarking
$$\text{GMV}_{\text{month}} = (\bar{V}_{\text{daily}} \times 30.4) \times \alpha \times \text{ATV} \times \left(0.85 + 0.30 \cdot \frac{\text{SVI}}{100}\right)$$
$$\text{Rent}_{\text{annual}}^{\max} = (\text{GMV}_{\text{month}} \times 12) \times \text{OCR}$$
$$\text{Rent / m}^2 = \frac{\text{Rent}_{\text{annual}}^{\max}}{\text{Area}_{\text{sqm}}}$$

---

## 4. Key Empirical Findings & Commercial Insights

### 4.1 Top Commercial Retail Catchments
1. **Flinders La-Swanston St (West)** — SVI: **83.72** (Tier 1 Flagship Catchment) | Est. Annual GMV: **$34.40M AUD**
2. **Flinders St-Elizabeth St (East)** — SVI: **79.69** (Tier 2 High-Yield Hub) | Est. Annual GMV: **$15.82M AUD**
3. **Town Hall (West)** — SVI: **79.07** (Tier 2 High-Yield Hub) | Est. Annual GMV: **$25.61M AUD**

### 4.2 Shock Resilience Under Urban Stress
* **Most Resilient Assets**: Enclosed retail concourses (e.g. Melbourne Central: RSI 83.50) benefit from weather refuge (+25% rain surge) and diversified commuter/leisure footfall.
* **Most Vulnerable Assets**: Open-bridge and transit-exclusive platforms (e.g. Bourke St Bridge: RSI 47.15) suffer during transit strikes (-65%) and torrential rain (-38%).

---

## 5. Verification & Testing

To execute all tests and ensure 100% pass rate:
```powershell
python -m unittest discover tests
```
*Result: 10/10 tests passed cleanly in 0.145s.*
