"""Run a bounded initial exploration of the GeoPulse source datasets."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
REPORT_PATH = ROOT / "reports" / "dataset_exploration.txt"
CHUNK_SIZE = 100_000

HOURLY_FILENAME = (
    "Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv"
)
LOCATIONS_FILENAME = "Pedestrian_Counting_System_-_Sensor_Locations.csv"


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Required dataset not found: {path}")


def count_csv_records(path: Path) -> int:
    """Count CSV records with bounded memory, without loading them into Pandas."""
    newline_count = 0
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            newline_count += block.count(b"\n")
        source.seek(0, 2)
        if source.tell():
            source.seek(-1, 2)
            if source.read(1) != b"\n":
                newline_count += 1
    return max(0, newline_count - 1)


def normalize_identifier(value: object) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)) and float(value).is_integer():
        return str(int(value))
    return str(value).strip()


def sensor_id_column(columns: list[str]) -> str | None:
    for column in columns:
        normalized = column.lower().replace(" ", "_")
        if "sensor" in normalized and "id" in normalized:
            return column
    return None


def inspect_hourly(path: Path) -> dict[str, object]:
    reader = pd.read_csv(
        path, chunksize=CHUNK_SIZE, encoding="utf-8-sig"
    )
    sample = next(reader, None)
    if sample is None:
        raise ValueError(f"No data rows found in pedestrian dataset: {path}")

    numeric = sample.select_dtypes(include=np.number)
    sensor_column = sensor_id_column(list(sample.columns))
    sensor_ids = set()
    if sensor_column:
        sensor_ids = {
            identifier
            for value in sample[sensor_column].dropna().unique()
            if (identifier := normalize_identifier(value)) is not None
        }

    date_ranges = {}
    for column in sample.columns:
        is_date_text = (
            "date" in column.lower() or "timestamp" in column.lower()
        ) and not pd.api.types.is_numeric_dtype(sample[column])
        if is_date_text:
            parsed = pd.to_datetime(
                sample[column], format="mixed", errors="coerce"
            ).dropna()
            date_ranges[column] = (
                str(parsed.min()) if not parsed.empty else "unavailable",
                str(parsed.max()) if not parsed.empty else "unavailable",
            )

    return {
        "sample": sample,
        "numeric": numeric,
        "missing": sample.isna().sum(),
        "sample_duplicates": int(sample.duplicated().sum()),
        "sensor_column": sensor_column,
        "sensor_ids": sensor_ids,
        "date_ranges": date_ranges,
    }


def format_frame(frame: pd.DataFrame) -> str:
    return frame.to_string(index=False, max_cols=None, max_colwidth=40)


def build_report(
    hourly_path: Path,
    hourly_rows: int,
    hourly: dict[str, object],
    locations_path: Path,
    locations: pd.DataFrame,
) -> str:
    sample = hourly["sample"]
    sample_ids = hourly["sensor_ids"]
    hourly_sensor_column = hourly["sensor_column"]
    location_sensor_column = sensor_id_column(list(locations.columns))
    location_ids = set()
    if location_sensor_column:
        location_ids = {
            identifier
            for value in locations[location_sensor_column].dropna().unique()
            if (identifier := normalize_identifier(value)) is not None
        }

    common_ids = sample_ids & location_ids
    count_columns = [
        column
        for column in hourly["numeric"].columns
        if "count" in column.lower() or "pedestrian" in column.lower()
    ]

    lines = [
        "GeoPulse – Hyper-Local Retail Mobility Analytics",
        "Dataset Exploration Report",
        "=" * 58,
        "",
        "Dataset descriptions",
        "1. Pedestrian counting: monthly pedestrian counts recorded per hour.",
        "2. Sensor locations: sensor identifiers, descriptive/location "
        "attributes, and coordinates where provided.",
        "",
        "1. Pedestrian counting dataset",
        f"File: data/raw/{HOURLY_FILENAME}",
        f"File size: {hourly_path.stat().st_size:,} bytes",
        f"Dimensions: {hourly_rows:,} rows × "
        f"{len(sample.columns)} columns",
        f"Inspection sample: first {len(sample):,} rows, read as one "
        f"{CHUNK_SIZE:,}-row Pandas chunk.",
        "Columns and sample dtypes:",
    ]
    lines.extend(
        f"  - {column}: {dtype}"
        for column, dtype in sample.dtypes.items()
    )
    lines.extend(["", "First five records:", format_frame(sample.head(5))])
    lines.extend(["", "Missing values in inspected sample:"])
    lines.extend(
        f"  - {column}: {int(count):,}"
        for column, count in hourly["missing"].items()
    )
    lines.extend(
        [
            f"Full-row duplicates in inspected sample: "
            f"{hourly['sample_duplicates']:,}",
            "Full-dataset duplicate check: skipped to keep this initial "
            "inspection bounded.",
            "",
            "Numeric descriptive statistics for inspected sample:",
        ]
    )
    if hourly["numeric"].empty:
        lines.append("  - No numeric columns detected in the sample.")
    else:
        lines.append(hourly["numeric"].describe().to_string())

    if count_columns:
        lines.append("")
        lines.append("Pedestrian/count columns detected in the sample:")
        for column in count_columns:
            lines.append(
                f"  - {column}: sample total="
                f"{hourly['numeric'][column].sum():,.0f}"
            )
    lines.append(
        "Date/time fields in the inspected sample: "
        + (
            ", ".join(
                f"{column} ({bounds[0]} to {bounds[1]})"
                for column, bounds in hourly["date_ranges"].items()
            )
            if hourly["date_ranges"]
            else "none detected"
        )
    )
    lines.append(
        f"Sensor identification in sample: {hourly_sensor_column or 'not detected'}; "
        f"{len(sample_ids):,} distinct non-missing IDs."
    )

    lines.extend(
        [
            "",
            "2. Sensor location dataset",
            f"File: data/raw/{LOCATIONS_FILENAME}",
            f"File size: {locations_path.stat().st_size:,} bytes",
            f"Dimensions: {len(locations):,} rows × {len(locations.columns)} columns",
            "Columns and dtypes:",
        ]
    )
    lines.extend(
        f"  - {column}: {dtype}"
        for column, dtype in locations.dtypes.items()
    )
    lines.extend(
        ["", "First five records:", format_frame(locations.head(5))]
    )
    lines.append("Missing values (full location dataset):")
    lines.extend(
        f"  - {column}: {int(count):,}"
        for column, count in locations.isna().sum().items()
    )
    lines.append(
        f"Full-row duplicate records: {int(locations.duplicated().sum()):,}"
    )
    lines.extend(
        ["", "Descriptive statistics (full location dataset):",
         locations.describe(include="all").to_string(max_cols=None)]
    )
    if location_sensor_column:
        lines.append(
            f"Sensor identification: {location_sensor_column}; "
            f"{len(location_ids):,} distinct IDs; "
            f"{int(locations[location_sensor_column].duplicated().sum()):,} "
            "repeated ID values."
        )
    coordinates = [
        column
        for column in locations.columns
        if column.lower() in {"latitude", "longitude"}
    ]
    lines.append(
        "Geographical columns: "
        + (", ".join(coordinates) if coordinates else "none detected")
    )

    lines.extend(
        [
            "",
            "3. Potential relationship",
            f"Sensor-ID columns: pedestrian {hourly_sensor_column or 'not detected'}; "
            f"locations {location_sensor_column or 'not detected'}.",
            f"Distinct sensor IDs shared by the inspected pedestrian sample "
            f"and location dataset: {len(common_ids):,}.",
            "These common identifiers can link sample hourly counts to "
            "sensor metadata and coordinates.",
            "",
            "Limitations",
            "Pedestrian missing-value counts, duplicate counts, numeric "
            "statistics, and sensor-ID coverage describe only the first "
            f"{len(sample):,} rows. Full pedestrian duplicate analysis was "
            "intentionally skipped. The total row count is counted with "
            "bounded-memory file streaming.",
            "Source CSV files were read only and were not modified.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    hourly_path = RAW_DIR / HOURLY_FILENAME
    locations_path = RAW_DIR / LOCATIONS_FILENAME

    try:
        require_file(hourly_path)
        require_file(locations_path)
        print("Inspecting a bounded pedestrian sample...")
        hourly_rows = count_csv_records(hourly_path)
        hourly = inspect_hourly(hourly_path)
        print("Reading the small sensor-location dataset...")
        locations = pd.read_csv(locations_path, encoding="utf-8-sig")

        report = build_report(
            hourly_path, hourly_rows, hourly, locations_path, locations
        )
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print("Exploration completed successfully.")
        print(
            f"Pedestrian dataset: {hourly_rows:,} rows, "
            f"{len(hourly['sample'].columns)} columns; "
            f"{len(hourly['sample']):,}-row sample."
        )
        print(
            f"Sensor locations: {len(locations):,} rows, "
            f"{len(locations.columns)} columns."
        )
        print(f"Report created: {REPORT_PATH.relative_to(ROOT)}")
        return 0
    except (
        OSError,
        ValueError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
    ) as error:
        print(f"Dataset exploration failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
