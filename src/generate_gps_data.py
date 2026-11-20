
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

# ==========================================
# 1. DATASET SETTINGS
# ==========================================

total_records = 50000
total_devices = 1000

CENTER_LAT = -37.8136
CENTER_LON = 144.9631

# Melbourne CBD area boundaries
MIN_LAT, MAX_LAT = -37.90, -37.75
MIN_LON, MAX_LON = 144.85, 145.05

device_ids = [
    f"DEV{str(i).zfill(5)}"
    for i in range(1, total_devices + 1)
]


# ==========================================
# 2. GENERATE BOUNDED GPS COORDINATES
# ==========================================

def generate_bounded_normal(mean, std, size, minimum, maximum):
    """Generate coordinates within Melbourne boundaries."""

    values = []

    while len(values) < size:
        needed = size - len(values)

        candidates = np.random.normal(
            mean,
            std,
            needed * 2
        )

        valid = candidates[
            (candidates >= minimum) &
            (candidates <= maximum)
        ]

        values.extend(valid.tolist())

    return np.array(values[:size])


latitudes = generate_bounded_normal(
    CENTER_LAT, 0.015, total_records, MIN_LAT, MAX_LAT
)

longitudes = generate_bounded_normal(
    CENTER_LON, 0.015, total_records, MIN_LON, MAX_LON
)


# ==========================================
# 3. GENERATE TIMESTAMPS
# ==========================================

timestamps = pd.to_datetime(
    np.random.randint(
        pd.Timestamp("2026-10-01").timestamp(),
        pd.Timestamp("2026-11-01").timestamp(),
        total_records
    ),
    unit="s",
    utc=True
).tz_convert("Australia/Melbourne")


# ==========================================
# 4. CREATE GPS DATASET
# ==========================================

data = pd.DataFrame({
    "DeviceID": np.random.choice(device_ids, total_records),
    "Latitude": latitudes,
    "Longitude": longitudes,
    "Timestamp": timestamps,
    "Accuracy_Meters": np.random.randint(5, 36, total_records),
    "Data_Type": "SYNTHETIC"
})

data = data.sort_values("Timestamp").reset_index(drop=True)


# ==========================================
# 5. DUPLICATE RECORD VALIDATION
# ==========================================

duplicate_count = data.duplicated(
    subset=[
        "DeviceID",
        "Latitude",
        "Longitude",
        "Timestamp"
    ]
).sum()

data = data.drop_duplicates(
    subset=[
        "DeviceID",
        "Latitude",
        "Longitude",
        "Timestamp"
    ]
).reset_index(drop=True)


# ==========================================
# 6. MELBOURNE BOUNDARY VALIDATION
# ==========================================

invalid_coordinates = (
    (data["Latitude"] < MIN_LAT) |
    (data["Latitude"] > MAX_LAT) |
    (data["Longitude"] < MIN_LON) |
    (data["Longitude"] > MAX_LON)
)

invalid_count = invalid_coordinates.sum()

data = data.loc[~invalid_coordinates].copy()


# ==========================================
# 7. GLOBAL COORDINATE VALIDATION
# ==========================================

global_coordinate_errors = (
    (~data["Latitude"].between(-90, 90)) |
    (~data["Longitude"].between(-180, 180))
).sum()


# ==========================================
# 8. MISSING VALUE CHECK
# ==========================================

missing_values = data.isnull().sum()


# ==========================================
# 9. SAVE GENERATED DATASET
# ==========================================

output_folder = Path("data/raw")
output_folder.mkdir(parents=True, exist_ok=True)

output_file = (
    output_folder /
    "synthetic_gps_pings_generated.csv"
)

data.to_csv(output_file, index=False)


# ==========================================
# 10. DATA QUALITY REPORT
# ==========================================

print("\n======================================")
print(" MELBOURNE GPS DATA GENERATION REPORT")
print("======================================")

print("Expected Records:", total_records)
print("Final Records:", len(data))
print("Unique Devices:", data["DeviceID"].nunique())

print("\n========== DATA QUALITY CHECKS ==========")

print("Duplicate Records Removed:", duplicate_count)
print("Invalid Melbourne Coordinates:", invalid_count)
print("Global Coordinate Errors:", global_coordinate_errors)

print("\nMissing Values:")
print(missing_values)

print("\nLatitude Range:")
print(data["Latitude"].min(), "to", data["Latitude"].max())

print("\nLongitude Range:")
print(data["Longitude"].min(), "to", data["Longitude"].max())

print("\nTimestamp Timezone:")
print(data["Timestamp"].dt.tz)

print("\nFirst 5 Records:")
print(data.head())

print("\nDataset Saved At:", output_file)

print("\nMelbourne GPS Dataset Generated Successfully!")
