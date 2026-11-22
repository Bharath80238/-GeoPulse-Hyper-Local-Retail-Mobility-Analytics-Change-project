# GeoPulse: Executive Retail Catchment & Spatial Mobility Dossier
**Author**: Amit Prajapati (GitHub: `amit20055`)  
**Designated Role**: Member 3 — Spatial Mobility & Retail Catchment Analyst  
**Internship**: Infotact Solutions (Batch-22.1 | Ref: ITS/DA/1838)  
**Branch**: `Amit-Prajapati` | **Generated**: 2026-11-22 13:54:38  

---

## 1. Executive Summary & Core Deliverables

This dossier synthesizes the spatial-temporal telemetry of 91 pedestrian sensor nodes across the Melbourne Central Business District (CBD). By combining physical walking isochrones, footfall diurnal stability, and commercial elasticity, this framework delivers an end-to-end decision engine for corporate retail site selection, store cannibalization avoidance, and rental lease optimization.

### Key Macro Metrics:
* **Total Sensor Catchments Evaluated**: 58 active commercial nodes
* **Network Mean Store Viability Index (SVI)**: **56.49 / 100**
* **Total Estimated Network Retail Turnover**: **$228,083,392.66 AUD / year**
* **Critical Cannibalization Conflict Pairs**: **5 store pairs** requiring format differentiation
* **All-Weather High-Resilience Locations**: **25 sites** proven resistant to transit & weather shocks

---

## 2. Top Commercial Retail Catchments (SVI Rankings)

| Rank | Sensor / Location Name | Precinct | SVI Score | Viability Tier | Est. Annual GMV (AUD) |
|:---:|:---|:---|:---:|:---|:---:|
| 1 | **Flinders La-Swanston St (West)** | Central Retail Core (Bourke St Mall) | **83.72** | Tier 1 - Flagship Catchment | $34,395,491.39 |
| 2 | **Flinders St-Elizabeth St (East)** | Flinders Transit Hub (Commuter Spine) | **79.69** | Tier 2 - High-Yield Commercial Hub | $8,515,854.46 |
| 3 | **Town Hall (West)** | Central Retail Core (Bourke St Mall) | **79.07** | Tier 2 - High-Yield Commercial Hub | $25,605,548.39 |
| 4 | **Melbourne Central** | Central Retail Core (Bourke St Mall) | **76.65** | Tier 2 - High-Yield Commercial Hub | $18,994,350.12 |
| 5 | **Melbourne Central-Elizabeth St (East)** | Central Retail Core (Bourke St Mall) | **75.73** | Tier 2 - High-Yield Commercial Hub | $17,521,712.52 |

---

## 3. High-Risk Cannibalization Corridors

The following adjacent stores share substantial footfall catchments ($d \le 350	ext{m}$) with **Cannibalization Risk Index (CRI) $\ge 60$**:

* ⚠️ **Collins St (North)** &harr; **Australia on Collins** (27.3m apart) — **CRI: 82.83**
  * *Prescription*: Enforce single-store exclusivity; avoid sister franchise deployment within 300m
* ⚠️ **Collins Place (South)** &harr; **Collins Place (North)** (25.4m apart) — **CRI: 79.31**
  * *Prescription*: Enforce single-store exclusivity; avoid sister franchise deployment within 300m
* ⚠️ **Bourke Street Mall (South)** &harr; **Bourke Street Mall (North)** (34.7m apart) — **CRI: 76.54**
  * *Prescription*: Enforce single-store exclusivity; avoid sister franchise deployment within 300m
* ⚠️ **Elizabeth St-Lonsdale St (South)** &harr; **Lonsdale St - Elizabeth St (North)** (40.6m apart) — **CRI: 71.9**
  * *Prescription*: Enforce single-store exclusivity; avoid sister franchise deployment within 300m
* ⚠️ **Melbourne Central** &harr; **State Library** (44.1m apart) — **CRI: 64.41**
  * *Prescription*: Enforce single-store exclusivity; avoid sister franchise deployment within 300m

---

## 4. Tenant Category Allocation Strategy

Retail tenant matching reveals distinct spatial clustering:
* **Artisan Boutique & Specialty Retail**: 18 sites (Heritage laneways & peripheral streets)
* **QSR / Grab-and-Go Coffee**: 17 sites (High-velocity transit spines)
* **Everyday Convenience & Pharmacy**: 17 sites (Consistent daytime density)
* **Luxury & International Flagship**: 4 sites (Central Retail Core / Bourke St Mall)
* **Experiential Dining & Evening Lounge**: 2 sites (Southbank Waterfront & Chinatown)

---

## 5. Verification & Audit Trail

All analytical pipelines, database schemas, and output datasets are verified under `tests/test_mobility_analytics.py` with 100% test pass rate.
