# GeoPulse – Week 1 Data Validation Report
## 1. Project Overview
Project Name: GeoPulse – Hyper-Local Retail & Mobility Analytics
Objective: To validate pedestrian counts, sensor locations, and synthetic GPS datasets before performing data analysis.
## 2. Dataset Summary
| Dataset | Records | Columns |
|---|---:|---:|
| Pedestrian Counts | 10,000 | 10 |
| Sensor Locations | 91 | 11 |
| Synthetic GPS Pings | 50,000 | 6 |
## 3. Pedestrian Counts Validation
- Total records: 10,000
- Missing values detected: 0
- Duplicate IDs: 0
## 4. Sensor Locations Validation
- Total records: 91
- Missing values:
  - direction_1: 13
  - direction_2: 13
  - note: 81
- Duplicate sensor IDs: 0
- Missing values will be reviewed before analysis.
## 5. GPS Dataset Validation
- Total records: 50,000
- Missing values: 0
- Duplicate records (DeviceID + Timestamp): 0
- Invalid coordinates: 0
- Invalid accuracy values: 0
- Invalid timestamps: 0
- Data type: SYNTHETIC
- Latitude range: -37.850000 to -37.774038
- Longitude range: 144.924408 to 145.002945
Detailed GPS results: gps_validation_report.csv
## 6. Conclusion
Initial validation checks were completed for all three datasets. The GPS and pedestrian datasets passed the checks performed. The sensor dataset contains missing values in direction_1, direction_2, and note, which require review before further analysis.
## 7. Next Steps
1. Review missing values in sensor locations.
2. Perform data preprocessing.
3. Explore dataset distributions.
4. Prepare visualizations for mobility and pedestrian analysis.
