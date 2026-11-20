
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# 1. FILE PATHS
# ==========================================

input_file = Path("data/cleaned_gps_pings.csv")

report_folder = Path("reports/week2")
visualization_folder = Path("visualizations")

report_folder.mkdir(parents=True, exist_ok=True)
visualization_folder.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. LOAD GPS DATA
# ==========================================

gps = pd.read_csv(input_file)

print("GPS Dataset Loaded Successfully!")
print("Total Records:", len(gps))

# ==========================================
# 3. DATA PREPROCESSING
# ==========================================

required_columns = [
    "DeviceID",
    "Latitude",
    "Longitude",
    "Timestamp"
]

missing_columns = [
    col for col in required_columns
    if col not in gps.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

gps["Timestamp"] = pd.to_datetime(
    gps["Timestamp"],
    errors="coerce",
    utc=True
)

gps["Latitude"] = pd.to_numeric(
    gps["Latitude"], errors="coerce"
)

gps["Longitude"] = pd.to_numeric(
    gps["Longitude"], errors="coerce"
)

gps = gps.dropna(
    subset=required_columns
).copy()

# Validate geographic coordinates
gps = gps[
    gps["Latitude"].between(-90, 90) &
    gps["Longitude"].between(-180, 180)
].copy()

# Convert timestamps to Melbourne local time
gps["Timestamp"] = gps["Timestamp"].dt.tz_convert(
    "Australia/Melbourne"
)

gps = gps.sort_values(
    ["DeviceID", "Timestamp"]
).reset_index(drop=True)

# ==========================================
# 4. HOURLY MOBILITY ANALYSIS
# ==========================================

gps["Hour"] = gps["Timestamp"].dt.hour

hourly_mobility = (
    gps.groupby("Hour")
    .agg(
        Total_GPS_Pings=("DeviceID", "count"),
        Active_Devices=("DeviceID", "nunique")
    )
    .reset_index()
)

hourly_mobility.to_csv(
    report_folder / "hourly_mobility.csv",
    index=False
)

# ==========================================
# 5. GPS DISTANCE CALCULATION
# ==========================================

gps["Previous_Latitude"] = (
    gps.groupby("DeviceID")["Latitude"].shift(1)
)

gps["Previous_Longitude"] = (
    gps.groupby("DeviceID")["Longitude"].shift(1)
)

gps["Previous_Timestamp"] = (
    gps.groupby("DeviceID")["Timestamp"].shift(1)
)

# Haversine distance calculation
def haversine_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return (
        2 * earth_radius
        * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    )


gps["Distance_KM"] = haversine_distance(
    gps["Previous_Latitude"],
    gps["Previous_Longitude"],
    gps["Latitude"],
    gps["Longitude"]
)

# First observation for each device has no previous point
gps["Distance_KM"] = gps["Distance_KM"].fillna(0)

# ==========================================
# 6. MOVEMENT SPEED CALCULATION
# ==========================================

gps["Elapsed_Hours"] = (
    gps["Timestamp"] - gps["Previous_Timestamp"]
).dt.total_seconds() / 3600

gps["Speed_KMH"] = np.where(
    gps["Elapsed_Hours"] > 0,
    gps["Distance_KM"] / gps["Elapsed_Hours"],
    np.nan
)

# ==========================================
# 7. DEVICE-WISE MOBILITY ANALYSIS
# ==========================================

device_mobility = (
    gps.groupby("DeviceID")
    .agg(
        Total_GPS_Pings=("DeviceID", "count"),
        Total_Distance_KM=("Distance_KM", "sum"),
        Average_Speed_KMH=("Speed_KMH", "mean"),
        Maximum_Speed_KMH=("Speed_KMH", "max")
    )
    .reset_index()
)

device_mobility = device_mobility.round(3)

device_mobility.to_csv(
    report_folder / "device_mobility.csv",
    index=False
)

# ==========================================
# 8. OVERALL MOBILITY SUMMARY
# ==========================================

summary = pd.DataFrame({
    "Metric": [
        "Total GPS Records",
        "Total Unique Devices",
        "Total Distance KM",
        "Average Estimated Speed KMH",
        "Maximum Estimated Speed KMH",
        "Hourly Activity Records",
        "Missing Values"
    ],

    "Value": [
        len(gps),
        gps["DeviceID"].nunique(),
        round(gps["Distance_KM"].sum(), 3),
        round(gps["Speed_KMH"].mean(), 3),
        round(gps["Speed_KMH"].max(), 3),
        len(hourly_mobility),
        int(gps.isnull().sum().sum())
    ]
})

summary.to_csv(
    report_folder / "mobility_summary.csv",
    index=False
)

# ==========================================
# 9. HOURLY MOBILITY VISUALIZATION
# ==========================================

plt.figure(figsize=(12, 6))

plt.bar(
    hourly_mobility["Hour"],
    hourly_mobility["Total_GPS_Pings"]
)

plt.title("Hourly GPS Mobility Activity - Melbourne")
plt.xlabel("Hour of Day")
plt.ylabel("Total GPS Pings")
plt.xticks(range(24))
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    visualization_folder / "hourly_mobility.png",
    dpi=300
)

plt.close()

# ==========================================
# 10. TOP 10 ACTIVE DEVICES
# ==========================================

top_devices = device_mobility.sort_values(
    "Total_GPS_Pings",
    ascending=False
).head(10)

plt.figure(figsize=(12, 6))

plt.bar(
    top_devices["DeviceID"],
    top_devices["Total_GPS_Pings"]
)

plt.title("Top 10 Active GPS Devices")
plt.xlabel("Device ID")
plt.ylabel("Total GPS Pings")
plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    visualization_folder / "top_10_active_devices.png",
    dpi=300
)

plt.close()

# ==========================================
# 11. FINAL REPORT
# ==========================================

print("\n========== WEEK 2 GPS MOBILITY REPORT ==========")

print("\nOverall Summary:")
print(summary.to_string(index=False))

print("\nTop 10 Active Devices:")
print(top_devices.to_string(index=False))

print("\nHourly Mobility:")
print(hourly_mobility.to_string(index=False))

print("\nGenerated Files:")
print("- reports/week2/mobility_summary.csv")
print("- reports/week2/hourly_mobility.csv")
print("- reports/week2/device_mobility.csv")
print("- visualizations/hourly_mobility.png")
print("- visualizations/top_10_active_devices.png")

print("\nGPS Mobility Analysis Completed Successfully!")
