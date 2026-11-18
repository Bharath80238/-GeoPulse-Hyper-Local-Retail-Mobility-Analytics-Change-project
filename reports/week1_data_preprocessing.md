# GeoPulse – Week 1 Data Preprocessing Report
## 1. Introduction
Week 1 focused on data validation, cleaning, and preprocessing for the GeoPulse – Hyper-Local Retail & Mobility Analytics project.
## 2. Datasets Processed
| Dataset | Original Records | Cleaned Records |
|---|---:|---:|
| Sensor Locations | 91 | 91 |
| Synthetic GPS Pings | 50,000 | 50,000 |
| Pedestrian Counts | 10,000 | 10,000 |
| Total | 60,091 | 60,091 |
## 3. Sensor Locations Preprocessing
- Loaded and inspected 91 sensor records.
- Identified missing values in direction_1 (13), direction_2 (13), and note (81).
- Replaced missing direction_1 and direction_2 values with "Unknown" in the cleaned copy.
- Preserved the original raw dataset.
- Exported cleaned_sensor_locations.csv.
- Verified that no direction_1 or direction_2 values remain blank.
Note: Missing note values were left unchanged.
## 4. GPS Data Preprocessing
- Loaded 50,000 GPS records.
- Checked for missing values, duplicate records, invalid coordinates, invalid accuracy values, and invalid timestamps.
- Converted Latitude, Longitude, and Accuracy_Meters into numeric values.
- Converted Timestamp into DateTimeOffset values.
- Preserved timezone offsets.
- Exported cleaned_gps_pings.csv.
- Verified that all 50,000 records were retained.
## 5. Pedestrian Counts Preprocessing
- Loaded 10,000 pedestrian records.
- Checked date-time validity.
- Checked Hourly_Counts for invalid numeric and negative values.
- Converted ID, Sensor_ID, and Hourly_Counts into numeric types.
- Converted Date_Time into DateTime values.
- Exported cleaned_pedestrian_counts.csv.
- Verified that all 10,000 records were retained.
## 6. Final Verification
| Cleaned Dataset | Records | Verification |
|---|---:|---|
| cleaned_sensor_locations.csv | 91 | Passed |
| cleaned_gps_pings.csv | 50,000 | Passed |
| cleaned_pedestrian_counts.csv | 10,000 | Passed |
Total cleaned records: 60,091.
## 7. Output Files
- data/cleaned_sensor_locations.csv
- data/cleaned_gps_pings.csv
- data/cleaned_pedestrian_counts.csv
## 8. Conclusion
Week 1 data preprocessing successfully produced three cleaned datasets. All original records were retained, and the cleaned files were exported and verified. These datasets are ready for further exploratory data analysis and integration.
