# Week 2 – GPS Mobility and Spatial Analysis

## 1. Objective

The objective of Week 2 was to analyze GPS mobility patterns and identify spatial activity patterns using GPS ping data, sensor location data, and pedestrian count data.

## 2. GPS Mobility Analysis

GPS mobility analysis was performed to understand device activity and movement patterns.

### Key Activities

- Analyzed 50,000 GPS records.
- Identified 2,000 unique GPS devices.
- Calculated hourly mobility patterns.
- Analyzed device-level mobility.
- Estimated movement speed using consecutive GPS observations.
- Identified the top 10 most active devices.

### Generated Reports

- `hourly_mobility.csv`
- `device_mobility.csv`
- `mobility_summary.csv`

### Generated Visualizations

- `hourly_mobility.png`
- `top_10_active_devices.png`

## 3. Spatial Analysis

Spatial analysis was performed to understand the geographical distribution of GPS records and pedestrian activity across sensor locations.

### Dataset Overview

- GPS Records: 50,000
- Unique GPS Devices: 2,000
- Sensor Locations: 91
- Pedestrian Count Records: 10,000
- GPS Spatial Density Grids: 3,088

### Key Activities

- Analyzed GPS latitude and longitude ranges.
- Aggregated pedestrian counts by sensor ID.
- Combined pedestrian activity data with sensor location information.
- Identified the top 10 busiest sensor locations.
- Generated GPS spatial density grids.
- Visualized GPS distribution and sensor activity patterns.

### Key Findings

- The busiest sensor location was **Flinders St–Elizabeth St (East)**.
- Its total pedestrian count was **289,217**.
- GPS coordinates covered the latitude range from -37.850000 to -37.774038.
- GPS coordinates covered the longitude range from 144.924408 to 145.002945.

### Generated Reports

- `gps_spatial_summary.csv`
- `sensor_activity.csv`
- `top_10_spatial_sensors.csv`
- `gps_spatial_density.csv`

### Generated Visualizations

- `gps_spatial_heatmap.png`
- `sensor_location_map.png`
- `top_10_spatial_sensors.png`

## 4. Tools and Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- GPS Data Analysis
- Spatial Data Analysis
- CSV Data Processing

## 5. Conclusion

Week 2 successfully completed GPS mobility analysis and spatial analysis. The analysis provided insights into device activity, estimated movement patterns, GPS geographical distribution, and pedestrian activity across sensor locations.

The generated CSV reports and visualizations provide a foundation for further mobility and retail location analysis in the upcoming project phases.

## 6. Week 2 Day 2 – Detailed Analysis and Validation

The second day focused on improving GPS mobility analysis,
spatial density analysis, and sensor activity visualization.

### Mobility Analysis Improvements

- Generated device-level mobility information.
- Analyzed hourly activity distribution.
- Organized mobility summary reports.
- Created visualizations for active devices.

### Spatial Analysis Improvements

- Generated GPS spatial density grids.
- Analyzed sensor-level pedestrian activity.
- Identified the top 10 active spatial sensors.
- Created a GPS spatial heatmap.
- Generated a sensor location map.

### Output Validation

All generated CSV reports and visualization files
were organized under the reports/week2 directory.

These outputs will support further retail mobility
analysis and help identify high-activity geographical areas.

### Next Steps

- Explore retail hotspot identification.
- Analyze geographical movement patterns.
- Prepare insights for the next project phase.