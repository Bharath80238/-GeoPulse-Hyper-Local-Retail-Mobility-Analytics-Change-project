
import pandas as pd
from pathlib import Path

# ==========================================
# 1. FILE PATHS
# ==========================================

input_file = Path("data/cleaned_gps_pings.csv")
report_folder = Path("reports/week2")

report_folder.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. LOAD DATA
# ==========================================

gps = pd.read_csv(input_file)

original_records = len(gps)

print("GPS Dataset Loaded Successfully!")
print("Original Records:", original_records)

# ==========================================
# 3. CHECK REQUIRED COLUMNS
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
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# ==========================================
# 4. MISSING VALUE ANALYSIS
# ==========================================

missing_report = gps.isnull().sum()

# ==========================================
# 5. DUPLICATE RECORD ANALYSIS
# ==========================================

duplicate_records = gps.duplicated().sum()

# ==========================================
# 6. COORDINATE VALIDATION
# ==========================================

gps["Latitude"] = pd.to_numeric(
    gps["Latitude"], errors="coerce"
)

gps["Longitude"] = pd.to_numeric(
    gps["Longitude"], errors="coerce"
)

invalid_latitude = (
    ~gps["Latitude"].between(-90, 90)
).sum()

invalid_longitude = (
    ~gps["Longitude"].between(-180, 180)
).sum()

# ==========================================
# 7. TIMESTAMP VALIDATION
# ==========================================

parsed_timestamp = pd.to_datetime(
    gps["Timestamp"],
    format="%d-%m-%Y %H:%M:%S %z",
    errors="coerce",
    utc=True
)


invalid_timestamps = parsed_timestamp.isna().sum()

# ==========================================
# 8. DATA QUALITY REPORT
# ==========================================

report = pd.DataFrame([
    {
        "Check": "Total GPS Records",
        "Count": original_records
    },
    {
        "Check": "Duplicate Records",
        "Count": int(duplicate_records)
    },
    {
        "Check": "Invalid Latitude",
        "Count": int(invalid_latitude)
    },
    {
        "Check": "Invalid Longitude",
        "Count": int(invalid_longitude)
    },
    {
        "Check": "Invalid Timestamps",
        "Count": int(invalid_timestamps)
    }
])

missing_data_report = pd.DataFrame({
    "Check": [
        f"Missing Values - {column}"
        for column in missing_report.index
    ],
    "Count": missing_report.values
})

final_report = pd.concat(
    [report, missing_data_report],
    ignore_index=True
)

# ==========================================
# 9. SAVE REPORT
# ==========================================

output_file = (
    report_folder / "data_quality_report.csv"
)

final_report.to_csv(
    output_file,
    index=False
)

# ==========================================
# 10. DISPLAY RESULTS
# ==========================================

print("\n========== DATA QUALITY REPORT ==========")

print(final_report.to_string(index=False))

print("\nReport Generated:")
print(output_file)

print("\nData Quality Validation Completed!")
