
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

# Dataset settings
total_records = 50000
total_devices = 1000

device_ids = [
    f"DEV{str(i).zfill(5)}"
    for i in range(1, total_devices + 1)
]

# Melbourne CBD coordinates
data = pd.DataFrame({
    "DeviceID": np.random.choice(device_ids, total_records),
    "Latitude": np.random.normal(-37.8136, 0.015, total_records),
    "Longitude": np.random.normal(144.9631, 0.015, total_records),
    "Timestamp": pd.to_datetime(
        np.random.randint(
            pd.Timestamp("2026-10-01").timestamp(),
            pd.Timestamp("2026-11-01").timestamp(),
            total_records
        ),
        unit="s",
        utc=True
    ).tz_convert("Australia/Melbourne"),
    "Accuracy_Meters": np.random.randint(5, 36, total_records),
    "Data_Type": "SYNTHETIC"
})

data = data.sort_values("Timestamp")

output_folder = Path("data/raw")
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "synthetic_gps_pings_generated.csv"
data.to_csv(output_file, index=False)

print("Melbourne GPS Dataset Generated Successfully!")
print("Total Records:", len(data))
print("Total Devices:", data["DeviceID"].nunique())
print("Missing Values:\n", data.isnull().sum())
print("\nFirst 5 Records:")
print(data.head())
print("\nSaved at:", output_file)

