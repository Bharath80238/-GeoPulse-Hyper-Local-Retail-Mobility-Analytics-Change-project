# Week 2 Output Validation Report

## 1. Validation Overview

- CSV files found: 8
- Chart files found: 5
- Total CSV records: 5205

## 2. CSV Validation Results

| File | Rows | Columns | Missing Cells | Duplicate Rows | Status |
|---|---:|---:|---:|---:|---|
| data_quality_report.csv | 11 | 2 | 0 | 0 | PASS |
| device_mobility.csv | 2000 | 5 | 0 | 0 | PASS |
| gps_spatial_density.csv | 3088 | 3 | 0 | 0 | PASS |
| gps_spatial_summary.csv | 6 | 2 | 0 | 0 | PASS |
| hourly_mobility.csv | 24 | 3 | 0 | 0 | PASS |
| mobility_summary.csv | 10 | 2 | 0 | 0 | PASS |
| sensor_activity.csv | 56 | 9 | 0 | 0 | PASS |
| top_10_spatial_sensors.csv | 10 | 9 | 0 | 0 | PASS |

## 3. Visualization Validation

- PASS: `gps_spatial_heatmap.png`
- PASS: `hourly_mobility.png`
- PASS: `sensor_location_map.png`
- PASS: `top_10_active_devices.png`
- PASS: `top_10_spatial_sensors.png`

## 4. Validation Scope

- CSV file existence and readability
- Record and column counts
- Missing cell counts
- Duplicate row counts
- PNG chart file existence

## 5. Conclusion

This report summarizes the structural validation of Week 2 analysis outputs. Missing values and duplicate rows are reported for further investigation where necessary.

Note: This is a structural validation, not a complete verification of analytical correctness.