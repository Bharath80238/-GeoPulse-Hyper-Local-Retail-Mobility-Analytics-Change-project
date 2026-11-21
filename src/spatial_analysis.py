
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# 1. FILE PATHS
# ==========================================

gps_file = Path("data/cleaned_gps_pings.csv")
sensor_file = Path("data/cleaned_sensor_locations.csv")
pedestrian_file = Path("data/cleaned_pedestrian_counts.csv")

report_folder = Path("reports/week2")
visualization_folder = Path("reports/week2/charts")

report_folder.mkdir(parents=True, exist_ok=True)
visualization_folder.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. LOAD DATASETS
# ==========================================

gps = pd.read_csv(gps_file)
sensors = pd.read_csv(sensor_file)
pedestrian = pd.read_csv(pedestrian_file)

print("All Spatial Datasets Loaded Successfully!")

print("GPS Records:", len(gps))
print("Sensor Records:", len(sensors))
print("Pedestrian Records:", len(pedestrian))

# ==========================================
# 3. DATA PREPROCESSING
# ==========================================

gps["Latitude"] = pd.to_numeric(
    gps["Latitude"], errors="coerce"
)

gps["Longitude"] = pd.to_numeric(
    gps["Longitude"], errors="coerce"
)

sensors["latitude"] = pd.to_numeric(
    sensors["latitude"], errors="coerce"
)

sensors["longitude"] = pd.to_numeric(
    sensors["longitude"], errors="coerce"
)

pedestrian["Sensor_ID"] = pd.to_numeric(
    pedestrian["Sensor_ID"], errors="coerce"
)

pedestrian["Hourly_Counts"] = pd.to_numeric(
    pedestrian["Hourly_Counts"], errors="coerce"
)

sensors["sensor_id"] = pd.to_numeric(
    sensors["sensor_id"], errors="coerce"
)

# Remove invalid GPS coordinates
gps = gps.dropna(
    subset=["Latitude", "Longitude"]
)

gps = gps[
    gps["Latitude"].between(-90, 90) &
    gps["Longitude"].between(-180, 180)
].copy()

# Remove invalid sensor coordinates
sensors = sensors.dropna(
    subset=["sensor_id", "latitude", "longitude"]
)

sensors = sensors[
    sensors["latitude"].between(-90, 90) &
    sensors["longitude"].between(-180, 180)
].copy()

# Remove missing pedestrian values
pedestrian = pedestrian.dropna(
    subset=["Sensor_ID", "Hourly_Counts"]
).copy()

# ==========================================
# 4. GPS SPATIAL DISTRIBUTION
# ==========================================

gps_spatial_summary = pd.DataFrame({
    "Metric": [
        "Total GPS Records",
        "Unique GPS Devices",
        "Minimum Latitude",
        "Maximum Latitude",
        "Minimum Longitude",
        "Maximum Longitude"
    ],

    "Value": [
        len(gps),
        gps["DeviceID"].nunique(),
        gps["Latitude"].min(),
        gps["Latitude"].max(),
        gps["Longitude"].min(),
        gps["Longitude"].max()
    ]
})

gps_spatial_summary.to_csv(
    report_folder / "gps_spatial_summary.csv",
    index=False
)

# ==========================================
# 5. PEDESTRIAN SENSOR ACTIVITY
# ==========================================

sensor_activity = (
    pedestrian.groupby("Sensor_ID")
    .agg(
        Total_Pedestrian_Count=("Hourly_Counts", "sum"),
        Average_Hourly_Count=("Hourly_Counts", "mean"),
        Maximum_Hourly_Count=("Hourly_Counts", "max"),
        Total_Observations=("Hourly_Counts", "count")
    )
    .reset_index()
)

# Join sensor locations and descriptions
sensor_activity = sensor_activity.merge(
    sensors[
        ["sensor_id", "sensor_name", "sensor_description",
         "latitude", "longitude"]
    ],
    left_on="Sensor_ID",
    right_on="sensor_id",
    how="left"
)

sensor_activity = sensor_activity.drop(
    columns=["sensor_id"]
)

sensor_activity = sensor_activity.sort_values(
    "Total_Pedestrian_Count",
    ascending=False
)

sensor_activity.to_csv(
    report_folder / "sensor_activity.csv",
    index=False
)

# ==========================================
# 6. TOP 10 BUSIEST SENSOR LOCATIONS
# ==========================================

top_sensors = sensor_activity.dropna(
    subset=["latitude", "longitude"]
).head(10)

top_sensors.to_csv(
    report_folder / "top_10_spatial_sensors.csv",
    index=False
)

# ==========================================
# 7. GPS SPATIAL DENSITY ANALYSIS
# ==========================================

gps["Latitude_Grid"] = (
    gps["Latitude"] * 1000
).round() / 1000

gps["Longitude_Grid"] = (
    gps["Longitude"] * 1000
).round() / 1000

gps_density = (
    gps.groupby(
        ["Latitude_Grid", "Longitude_Grid"]
    )
    .size()
    .reset_index(name="GPS_Ping_Count")
    .sort_values("GPS_Ping_Count", ascending=False)
)

gps_density.to_csv(
    report_folder / "gps_spatial_density.csv",
    index=False
)

# ==========================================
# 8. GPS DENSITY HEATMAP
# ==========================================

plt.figure(figsize=(10, 7))

plt.hist2d(
    gps["Longitude"],
    gps["Latitude"],
    bins=40,
    cmap="hot"
)

plt.colorbar(label="GPS Ping Density")

plt.title("Melbourne GPS Spatial Density Heatmap")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

plt.savefig(
    visualization_folder / "gps_spatial_heatmap.png",
    dpi=300
)

plt.close()

# ==========================================
# 9. SENSOR LOCATION MAP
# ==========================================

plt.figure(figsize=(11, 8))

plt.scatter(
    sensors["longitude"],
    sensors["latitude"],
    alpha=0.6,
    s=30,
    label="Sensor Locations"
)

plt.scatter(
    gps["Longitude"].sample(
        min(5000, len(gps)),
        random_state=42
    ),
    gps["Latitude"].sample(
        min(5000, len(gps)),
        random_state=42
    ),
    alpha=0.25,
    s=8,
    label="Synthetic GPS Points"
)

plt.title("Melbourne GPS and Sensor Locations")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    visualization_folder / "sensor_location_map.png",
    dpi=300
)

plt.close()

# ==========================================
# 10. TOP 10 PEDESTRIAN SENSOR CHART
# ==========================================

plt.figure(figsize=(12, 7))

plt.barh(
    top_sensors["sensor_description"].fillna(
        top_sensors["Sensor_ID"].astype(str)
    ).iloc[::-1],
    top_sensors["Total_Pedestrian_Count"].iloc[::-1]
)

plt.title("Top 10 Busiest Pedestrian Sensor Locations")
plt.xlabel("Total Pedestrian Count")
plt.ylabel("Sensor Location")

plt.tight_layout()

plt.savefig(
    visualization_folder / "top_10_spatial_sensors.png",
    dpi=300
)

plt.close()

# ==========================================
# 11. FINAL SPATIAL ANALYSIS REPORT
# ==========================================

print("\n========== WEEK 2 SPATIAL ANALYSIS ==========")

print("\nGPS Spatial Summary:")
print(gps_spatial_summary.to_string(index=False))

print("\nTop 10 Busiest Sensor Locations:")
print(top_sensors[
    ["Sensor_ID", "sensor_description",
     "Total_Pedestrian_Count"]
].to_string(index=False))

print("\nTotal GPS Density Grids:", len(gps_density))

print("\nGenerated Reports:")
print("- gps_spatial_summary.csv")
print("- sensor_activity.csv")
print("- top_10_spatial_sensors.csv")
print("- gps_spatial_density.csv")

print("\nGenerated Visualizations:")
print("- gps_spatial_heatmap.png")
print("- sensor_location_map.png")
print("- top_10_spatial_sensors.png")

print("\nSpatial Analysis Completed Successfully!")
