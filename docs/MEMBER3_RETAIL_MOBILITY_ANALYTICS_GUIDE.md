# Member 3: Spatial Mobility & Retail Catchment Analytics Guide
**Project**: GeoPulse: Hyper-Local Retail Mobility Analytics  
**Intern**: Amit Prajapati (GitHub: `amit20055` | Email: `amitprajapati0458@gmail.com`)  
**Designated Role**: Member 3 — Spatial Mobility & Retail Catchment Analyst  
**Organization**: Infotact Solutions (Batch-22.1 | Ref: ITS/DA/1838)  
**Branch**: `Amit-Prajapati`  

---

## 1. Executive Role Overview & Scope

As **Member 3 (Spatial Mobility & Retail Catchment Analyst)** on Project 2 (*GeoPulse*), my core responsibilities encompass transforming raw urban sensor telemetry into actionable commercial intelligence for commercial real estate, retail site selection, footfall predictability, cannibalization prevention, and tenant format allocation.

### Core Objectives:
1. **Spatial Precinct Clustering**: Geo-reference 91 Melbourne CBD pedestrian sensors, calculate proximity metrics to the commercial core, and cluster sensors into distinct commercial retail precincts.
2. **Temporal Footfall Dynamics**: Model 24-hour diurnal curves, identify morning/evening peak rush hours, and compute weekend surge elasticity ratios ($E_w$).
3. **Store Viability Index (SVI)**: Formulate and implement a multi-factor scoring model that quantifies commercial retail suitability on a 0–100 scale.
4. **Pedestrian Isochrone & Spatial Gravity Catchment Modeling**: Model 300m, 600m, and 1000m pedestrian walking buffers with spatial gravity decay to estimate true footfall capture pools.
5. **Store Cannibalization & Co-Location Risk Engine**: Formulate the Cannibalization Risk Index (CRI) between proximate sensors ($d \le 350\text{m}$) to prevent revenue dilution among sister franchises.
6. **Interactive Geospatial Dashboard**: Provide an interactive Leaflet/CartoDB web map (`geopulse_interactive_catchment_map.html`) with precinct overlays, SVI tier coloring, isochrone buffers, and cannibalization conflict lines.
7. **Retail Tenant Allocation Matrix**: Match site micro-profiles with 5 retail tenant archetypes (*Luxury Flagship, QSR Express, Experiential Dining, Convenience/Pharmacy, Boutique Pop-Up*).

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
│   └── tenant_allocation_matrix.json         # Category allocation breakdown
├── src/
│   ├── ingest_mobility_data.py               # Chunked ingestion pipeline (418 MB CSV -> SQLite)
│   ├── spatial_clustering.py                 # Haversine distance & precinct clustering
│   ├── temporal_mobility.py                  # Diurnal curves & weekend elasticity engine
│   ├── store_viability_index.py              # Multi-factor SVI scoring algorithm
│   ├── catchment_isochrone.py                # Pedestrian isochrones & spatial gravity model
│   ├── cannibalization_risk.py               # Pairwise cannibalization risk engine (CRI)
│   ├── generate_interactive_map.py           # Standalone interactive Leaflet web map
│   └── tenant_site_recommender.py            # Retail tenant archetype matching engine
└── tests/
    └── test_mobility_analytics.py            # Automated unit test suite (7/7 tests pass)
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
Pedestrian gravity pull from neighboring nodes:
$$A_i = \sum_{j \neq i} \frac{V_j}{d_{ij}^\beta} \quad (\beta = 1.5)$$

### 3.5 Cannibalization Risk Index (CRI)
Quantifies revenue dilution between proximate sister stores within $350\text{m}$:
$$\text{CRI}_{ij} = 100 \times \left( \frac{\min(V_i, V_j)}{\max(V_i, V_j)} \right)^{0.5} \times \exp\left(-\frac{d_{ij}}{200}\right)$$

---

## 4. Key Empirical Findings & Commercial Insights

### 4.1 Top Commercial Retail Catchments
1. **Flinders La-Swanston St (West)** — SVI: **83.72** (Tier 1 Flagship Catchment)
2. **Flinders St-Elizabeth St (East)** — SVI: **79.69** (Tier 2 High-Yield Hub)
3. **Town Hall (West)** — SVI: **79.07** (Tier 2 High-Yield Hub)

### 4.2 High-Risk Cannibalization Hotspots
* **Collins St (North) <--> Australia on Collins**: Separation 27.3m, CRI = 82.83.
* **Collins Place (South) <--> Collins Place (North)**: Separation 25.4m, CRI = 79.31.
* **Bourke Street Mall (South) <--> Bourke Street Mall (North)**: Separation 34.7m, CRI = 76.54.
* *Strategic Rule*: Sister franchises should avoid identical concepts within 300m unless using differentiated formats (Flagship vs. Express Grab-and-Go).

### 4.3 Tenant Format Allocations
* **QSR / Grab-and-Go (29.3%)**: Concentrated along Elizabeth St & Flinders commuter spines.
* **Everyday Convenience / Pharmacy (29.3%)**: Stationed in high-stability, low-variance corridors.
* **Artisan Boutique / Specialty Retail (31.0%)**: Best suited for peripheral laneways and heritage arcades.
* **Luxury & International Flagship (6.9%)**: Clustered exclusively in Bourke St Mall & Collins St high-gravity zones.
* **Experiential Dining / Nightlife (3.4%)**: Dominates Southbank Promenade and Chinatown.

---

## 5. Verification & Testing

To execute all tests and ensure 100% pass rate:
```powershell
python -m unittest discover tests
```
*Result: 7/7 tests passed cleanly (0.045s).*
