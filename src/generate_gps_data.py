
import pandas as pd
import numpy as np
from pathlib import Path

# Reproducible random data
np.random.seed(42)

# Dataset settings
total_records = 50000
total_devices = 1000

# Generate device IDs
device_ids = [
    f"D{str(i).zfill(4)}"
    for i in range(1, total_devices + 1)
]

# Generate synthetic GPS pings around Patna
data = pd.DataFrame({
    "DeviceID": np.random.choice(device_ids, total_records),
    "Latitude": np.random.normal(25.6093, 0.015, total_records),
    "Longitude": np.random.normal(85.1376, 0.015, total_records),
    "Timestamp": pd.to_datetime(
        np.random.randint(
            pd.Timestamp("2026-10-01").timestamp(),
            pd.Timestamp("2026-10-31").timestamp(),
            total_records
        ),
        unit="s"
    )
})

# Sort records by timestamp
data = data.sort_values("Timestamp")

# Create output folder
output_folder = Path("data/raw")
output_folder.mkdir(parents=True, exist_ok=True)

# Save CSV
output_file = output_folder / "gps_pings.csv"
data.to_csv(output_file, index=False)

print("GPS Dataset Generated Successfully!")
print("Total Records:", len(data))
print("Total Devices:", data["DeviceID"].nunique())
print("Missing Values:\n", data.isnull().sum())
print("\nFirst 5 Records:")
print(data.head())
print("\nSaved at:", output_file)
