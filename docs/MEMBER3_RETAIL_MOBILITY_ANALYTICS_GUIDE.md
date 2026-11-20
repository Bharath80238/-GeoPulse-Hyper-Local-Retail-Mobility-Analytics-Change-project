# Member 3: Spatial Mobility & Retail Catchment Analytics Guide
**Project**: GeoPulse: Hyper-Local Retail Mobility Analytics  
**Intern**: Amit Prajapati (GitHub: `amit20055` | Email: `amitprajapati0458@gmail.com`)  
**Designated Role**: Member 3 — Spatial Mobility & Retail Catchment Analyst  
**Organization**: Infotact Solutions (Batch-22.1 | Ref: ITS/DA/1838)  
**Branch**: `Amit-Prajapati`  

---

## 1. Executive Role Overview & Scope

As **Member 3 (Spatial Mobility & Retail Catchment Analyst)** on Project 2 (*GeoPulse*), my core responsibilities encompass transforming raw urban sensor telemetry into actionable commercial intelligence for commercial real estate, retail site selection, and footfall predictability.

### Core Objectives:
1. **Spatial Precinct Clustering**: Geo-reference 91 Melbourne CBD pedestrian sensors, calculate proximity metrics to the commercial core, and cluster sensors into distinct commercial retail precincts.
2. **Temporal Footfall Dynamics**: Model 24-hour diurnal curves, identify morning/evening peak rush hours, and compute weekend surge elasticity ratios.
3. **Store Viability Index (SVI)**: Formulate and implement a proprietary, multi-factor scoring model that quantifies commercial retail suitability on a 0–100 scale.
4. **Data Warehouse & Unit Testing**: Build a resilient local analytical warehouse (`geopulse.db`) with full test coverage across spatial, temporal, and viability algorithms.

---

## 2. System Architecture & Modular Pipeline

The analytical framework developed in branch `Amit-Prajapati` is organized as follows:

```
GeoPulse/
├── data/
│   └── processed/
│       ├── geopulse.db                  # SQLite analytical warehouse (indexed)
│       └── pedestrian_mobility_sample.csv # 50K row sample for rapid profiling
├── docs/
│   └── MEMBER3_RETAIL_MOBILITY_ANALYTICS_GUIDE.md # Technical documentation
├── reports/
│   ├── data_ingestion_summary.json      # Ingestion audit and table schemas
│   ├── sensor_spatial_profile.csv       # 91 sensors with precinct & CBD distance
│   ├── retail_precinct_summary.json     # Precinct footfall volume & density tiers
│   ├── hourly_diurnal_curves.csv        # 24-hour citywide diurnal profile
│   ├── sensor_weekend_elasticity.csv    # Per-sensor weekend surge ratio
│   ├── temporal_patterns_summary.json   # Peak hours and daypart volume shares
│   ├── store_viability_rankings.csv     # Ranked retail catchments with SVI scores
│   └── store_viability_summary.json     # SVI distribution and tier breakdown
├── src/
│   ├── ingest_mobility_data.py          # Chunked ingestion pipeline (418 MB CSV -> SQLite)
│   ├── spatial_clustering.py            # Haversine distance & precinct clustering
│   ├── temporal_mobility.py             # Diurnal curves & weekend elasticity engine
│   └── store_viability_index.py         # Multi-factor SVI scoring algorithm
└── tests/
    └── test_mobility_analytics.py       # Automated unit test suite (100% pass)
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
where $\bar{V}$ denotes mean hourly pedestrian count across that day-type.

### 3.3 Traffic Stability Score ($S_{\text{stab}}$)
Stability is inversely proportional to the Coefficient of Variation ($CV = \sigma / \mu$):
$$CV = \frac{\sqrt{\frac{1}{N}\sum_{i=1}^N (x_i - \bar{x})^2}}{\bar{x}}$$
$$S_{\text{stab}} = 100 \times \left(1 - \frac{CV - CV_{\min}}{CV_{\max} - CV_{\min}}\right)$$

### 3.4 Store Viability Index (SVI)
The composite SVI score weights four distinct operational dimensions:
$$\text{SVI} = 0.35 \cdot S_{\text{vol}} + 0.25 \cdot S_{\text{stab}} + 0.20 \cdot S_{\text{surge}} + 0.20 \cdot S_{\text{precinct}}$$

Where:
* $S_{\text{vol}}$: Log-normalized hourly average footfall volume (35%).
* $S_{\text{stab}}$: Traffic consistency / resistance to off-peak troughs (25%).
* $S_{\text{surge}}$: Weekend trade elasticity (20%).
* $S_{\text{precinct}}$: Precinct-level commercial gravity and co-tenant synergy (20%).

---

## 4. Key Empirical Insights & Retail Site Tiering

### 4.1 Top Retail Catchments in Melbourne CBD
| Rank | Catchment / Sensor Name | Retail Precinct | SVI Score | Viability Tier |
|:---:|:---|:---|:---:|:---|
| **1** | Flinders La-Swanston St (West) | Central Retail Core (Bourke St Mall) | **83.72** | Tier 1 - Flagship Catchment |
| **2** | Flinders St-Elizabeth St (East) | Flinders Transit Hub (Commuter Spine) | **79.69** | Tier 2 - High-Yield Hub |
| **3** | Town Hall (West) | Central Retail Core (Bourke St Mall) | **79.07** | Tier 2 - High-Yield Hub |
| **4** | Melbourne Central | Central Retail Core (Bourke St Mall) | **76.65** | Tier 2 - High-Yield Hub |
| **5** | Melbourne Central-Elizabeth St | Central Retail Core (Bourke St Mall) | **75.73** | Tier 2 - High-Yield Hub |

### 4.2 Viability Tier Distribution
* **Tier 1 (Flagship Catchments, SVI $\ge$ 80)**: 1.7% of network — Premium international fashion, flagship electronics, high-capex flagships.
* **Tier 2 (High-Yield Commercial Hubs, SVI 65–79.9)**: 39.7% of network — Fast casual F&B, convenience retail, commuter-oriented services.
* **Tier 3 (Moderate Local Catchments, SVI 50–64.9)**: 22.4% of network — Boutiques, specialty bakeries, destination cafes.
* **Tier 4 (Peripheral / Low-Footfall, SVI < 50)**: 36.2% of network — Lower-cost dark kitchens, destination specialty services.

---

## 5. Verification & Testing

To reproduce all results and verify analytical integrity, execute:

```powershell
# 1. Run unit test suite
python -m unittest discover tests

# 2. Ingest mobility data into warehouse
python src/ingest_mobility_data.py

# 3. Compute spatial clustering
python src/spatial_clustering.py

# 4. Generate diurnal curves & elasticity
python src/temporal_mobility.py

# 5. Compute Store Viability Index rankings
python src/store_viability_index.py
```
All unit tests validate schema adherence, non-null values, diurnal curve 24-hour integrity, and SVI scoring bounds ($0 \le \text{SVI} \le 100$).
