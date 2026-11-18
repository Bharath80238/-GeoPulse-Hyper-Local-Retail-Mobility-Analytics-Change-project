# Retail Catchment Cannibalization Prevention & Co-Location Guidelines
**Project**: GeoPulse: Hyper-Local Retail Mobility Analytics  
**Author**: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)  
**Organization**: Infotact Solutions (Batch-22.1 | Ref: ITS/DA/1838)  
**Effective Date**: 18 November 2026  

---

## 1. Executive Summary & Problem Context

In dense urban commercial cores such as the Melbourne Central Business District (CBD), rapid retail network expansion carries significant risk of intra-brand customer cannibalization. When corporate brands open adjacent stores along the same pedestrian artery, revenue from the new site frequently draws from the existing store rather than capturing incremental market demand.

This technical guideline operationalizes spatial catchment overlap metrics, defines minimum distance separation buffers, and establishes mandatory format differentiation criteria for commercial retail portfolio expansion across Melbourne CBD precincts.

---

## 2. Quantitative Cannibalization Risk Model (CRI)

The GeoPulse Cannibalization Risk Index (CRI) quantifies spatial and volume competition between two store locations ($i$ and $j$):

$$\text{CRI}_{ij} = 100 \times \left( \frac{\min(V_i, V_j)}{\max(V_i, V_j)} \right)^{0.5} \times \exp\left(-\frac{d_{ij}}{\lambda}\right)$$

Where:
- $V_i, V_j$: Mean daily pedestrian footfall volume at locations $i$ and $j$.
- $d_{ij}$: Planar Euclidean distance separation (in meters) between store coordinates.
- $\lambda$: Spatial decay scale constant ($\lambda = 200.0\text{ m}$ calibrated for CBD pedestrian walking tolerance).

### Strategic Action Thresholds

| Planar Distance ($d_{ij}$) | Cannibalization Risk Index (CRI) | Risk Classification | Mandatory Real Estate Action |
|:---:|:---:|:---:|:---|
| **$d < 150\text{ m}$** | **$\ge 70.0$** | **Critical Conflict** | **Strict Territorial Exclusion**: No identical brand format may be licensed or leased. |
| **$150\text{ m} \le d < 350\text{ m}$** | **$35.0 - 69.9$** | **Moderate Overlap** | **Mandatory Format Bifurcation**: Approved only if format is differentiated (e.g., Flagship Experience vs Express Grab-and-Go). |
| **$d \ge 350\text{ m}$** | **$< 35.0$** | **Synergistic Catchment** | **Unrestricted Expansion**: Sites tap independent pedestrian catchments without revenue degradation. |

---

## 3. High-Conflict Empirical Case Studies (Melbourne CBD)

Empirical sensor telemetry across the Melbourne CBD reveals critical high-risk proximity pairings:

1. **Collins Street (North) $\leftrightarrow$ Australia on Collins**:
   - Distance: $27.3\text{ m}$
   - Footfall Volumes: $1,420\text{ pax/hr}$ vs $1,180\text{ pax/hr}$
   - Calculated CRI: **$82.83$** (Severe Conflict)
   - *Recommendation*: Prohibit identical quick-service food formats; restrict to premium sit-down retail vs convenience kiosk.

2. **Collins Place (South) $\leftrightarrow$ Collins Place (North)**:
   - Distance: $25.4\text{ m}$
   - Footfall Volumes: $890\text{ pax/hr}$ vs $760\text{ pax/hr}$
   - Calculated CRI: **$79.31$** (Severe Conflict)
   - *Recommendation*: Unify operations under a single anchor tenancy rather than competing internal footprints.

3. **Bourke Street Mall (South) $\leftrightarrow$ Bourke Street Mall (North)**:
   - Distance: $34.7\text{ m}$
   - Footfall Volumes: $2,850\text{ pax/hr}$ vs $2,410\text{ pax/hr}$
   - Calculated CRI: **$76.54$** (Severe Conflict)
   - *Recommendation*: High pedestrian density allows dual presence only if merchandise assortments target distinct demographics (e.g., youth fashion vs business formal).

---

## 4. Multi-Unit Expansion Protocol

Before executing any commercial real estate lease within the Melbourne CBD corridor:
1. Run `src/store_expansion_optimizer.py` to calculate exact CRI against all existing corporate stores.
2. Verify catchment spatial polygon boundaries via Voronoi tessellation.
3. Obtain clearance confirming projected portfolio revenue increase exceeds $1.35\times$ individual store operating costs.
