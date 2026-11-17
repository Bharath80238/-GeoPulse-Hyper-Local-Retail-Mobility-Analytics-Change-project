# Week 1 Technical Milestone: Spatial Mobility Baseline & Telemetry Infrastructure
**Project**: GeoPulse: Hyper-Local Retail Mobility Analytics  
**Author**: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)  
**Organization**: Infotact Solutions (Batch-22.1 | Ref: ITS/DA/1838)  
**Milestone Window**: 10 Nov 2026 – 17 Nov 2026  

---

## 1. Week 1 Objectives & Achievements

During Week 1 of Project 2 (*GeoPulse*), Member 3 successfully established the complete spatial foundation, ingestion architecture, and telemetry audit framework for the Melbourne Central Business District pedestrian sensor network:

1. **Analytical Data Warehouse Setup**:
   - Ingested raw 418 MB Melbourne counting telemetry into indexed SQLite storage (`geopulse.db`).
   - Defined spatial tables (`sensor_locations`) and indexed temporal tables (`hourly_pedestrian_counts`).

2. **Spatial Bounding & Coordinate Reference**:
   - Georeferenced 91 sensors within EPSG:4326 (WGS84).
   - Identified CBD retail centroid at Town Hall / Bourke St Mall intersection (-37.8136, 144.9631).
   - Mapped spatial boundary span of 3.8 km (north-south) by 4.2 km (east-west).

3. **Telemetry Health & Continuity Audit**:
   - Profiled sensor continuity across 91 locations.
   - Identified top high-fidelity telemetry nodes with zero-count rates $< 3.5\%$.

4. **Rush-Hour Acceleration & Velocity Dynamics**:
   - Modeled morning (07:00-09:00) and evening (16:00-18:00) pedestrian ramp rates.
   - Established baseline off-peak versus peak rush hour multipliers across commuter corridors.

5. **Laneway Permeability & Weather Attenuation**:
   - Formulated the Laneway Permeability Index (LPI) capturing pedestrian spillover into heritage arcades.
   - Modeled precipitation elasticity factors distinguishing covered retail shelters from open waterfronts.

---

## 2. Key Artifacts Produced in Week 1

| Artifact File | Description |
|:---|:---|
| `src/spatial_bounds_definition.py` | Melbourne CBD spatial bounding box and centroid calculator |
| `reports/melbourne_cbd_boundary_geometry.json` | Geometry manifest and quadrant distribution |
| `src/sensor_telemetry_audit.py` | Observation continuity and uptime analyzer |
| `reports/sensor_hardware_audit_report.csv` | Sensor-level telemetry health scorecard |
| `src/rush_hour_arrival_rate.py` | Rush-hour acceleration and peak flow model |
| `src/laneway_permeability.py` | Laneway footfall absorption and arcade permeability index |
| `src/precipitation_elasticity.py` | Precipitation elasticity and weather shelter modeling |

---

## 3. Week 1 Sign-Off
All Week 1 spatial baseline requirements are completed, tested, and validated on branch `Amit-Prajapati`.
