"""Clean a bounded preview of GeoPulse source data and report data quality."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import TextIO

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_PATH = ROOT / "reports" / "day3_data_cleaning_report.txt"
HOURLY_FILENAME = (
    "Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv"
)
LOCATIONS_FILENAME = "Pedestrian_Counting_System_-_Sensor_Locations.csv"
DEFAULT_MAX_ROWS = 50_000
DEFAULT_CHUNK_SIZE = 10_000
INTEGER_COLUMNS = {
    "id",
    "year",
    "mdate",
    "time",
    "sensor_id",
    "hourly_counts",
}


def standardize_column_names(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert column labels to lowercase snake_case without losing columns."""
    result = frame.copy()
    names = []
    for column in result.columns:
        name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", str(column))
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        names.append(re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower())
    if len(set(names)) != len(names):
        raise ValueError("Column-name standardization produced duplicate names.")
    result.columns = names
    return result


def require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")


def normalize_text_values(frame: pd.DataFrame) -> pd.DataFrame:
    """Trim text and turn whitespace-only values into missing values."""
    result = frame.copy()
    for column in result.select_dtypes(include=["object", "string"]).columns:
        values = result[column].astype("string").str.strip()
        result[column] = values.mask(values.eq(""), pd.NA)
    for column in ("month", "day", "direction_1", "direction_2"):
        if column in result.columns:
            result[column] = result[column].str.title()
    if "status" in result.columns:
        result["status"] = result["status"].str.upper()
    return result


def convert_numeric_columns(
    frame: pd.DataFrame, columns: set[str]
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Coerce numeric columns while counting non-missing values that fail."""
    result = frame.copy()
    failures: dict[str, int] = {}
    for column in sorted(columns & set(result.columns)):
        original = result[column]
        converted = pd.to_numeric(original, errors="coerce")
        failures[column] = int((original.notna() & converted.isna()).sum())
        non_missing = converted.dropna()
        if non_missing.empty or np.equal(
            np.mod(non_missing.to_numpy(dtype="float64"), 1), 0
        ).all():
            result[column] = converted.astype("Int64")
        else:
            result[column] = converted
    return result, failures


def parse_datetime_column(
    frame: pd.DataFrame, column: str
) -> tuple[pd.Series, int, int]:
    original = frame[column]
    parsed = pd.to_datetime(original, format="mixed", errors="coerce")
    invalid = int((original.notna() & parsed.isna()).sum())
    missing = int(original.isna().sum())
    return parsed, invalid, missing


def validate_coordinates(
    frame: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Convert coordinates and null out malformed or out-of-range values."""
    result = frame.copy()
    issues: dict[str, int] = {}
    for column, lower, upper in (
        ("latitude", -90.0, 90.0),
        ("longitude", -180.0, 180.0),
    ):
        original = result[column]
        numeric = pd.to_numeric(original, errors="coerce")
        malformed = original.notna() & numeric.isna()
        out_of_range = numeric.notna() & ~numeric.between(lower, upper)
        issues[f"{column}_malformed"] = int(malformed.sum())
        issues[f"{column}_out_of_range"] = int(out_of_range.sum())
        result[column] = numeric.mask(out_of_range | malformed, np.nan)
    issues["coordinate_pairs_incomplete"] = int(
        result[["latitude", "longitude"]].isna().any(axis=1).sum()
    )
    return result, issues


def clean_sensor_locations(
    path: Path,
) -> tuple[pd.DataFrame, dict[str, object]]:
    locations = pd.read_csv(path, encoding="utf-8-sig")
    original_rows = len(locations)
    locations = normalize_text_values(standardize_column_names(locations))
    require_columns(
        locations,
        {
            "sensor_id",
            "sensor_description",
            "sensor_name",
            "installation_date",
            "latitude",
            "longitude",
        },
        "Sensor location dataset",
    )

    missing_values = {
        column: int(count)
        for column, count in locations.isna().sum().items()
    }
    exact_duplicates = int(locations.duplicated(keep="first").sum())
    locations = locations.drop_duplicates(keep="first").copy()
    locations, numeric_failures = convert_numeric_columns(
        locations, {"sensor_id"}
    )
    sensor_id_values = locations["sensor_id"]
    invalid_sensor_id = sensor_id_values.notna() & (
        sensor_id_values.le(0)
        | (sensor_id_values.astype("Float64") % 1).ne(0)
    )
    locations.loc[invalid_sensor_id, "sensor_id"] = pd.NA
    locations["sensor_id"] = locations["sensor_id"].astype("Int64")

    installation_dates, invalid_dates, missing_dates = parse_datetime_column(
        locations, "installation_date"
    )
    locations["installation_date"] = installation_dates
    locations, coordinate_issues = validate_coordinates(locations)

    valid_sensor_ids = locations["sensor_id"].dropna()
    repeated_sensor_ids = int(valid_sensor_ids.duplicated(keep="first").sum())

    stats: dict[str, object] = {
        "original_rows": original_rows,
        "retained_rows": len(locations),
        "removed_rows": exact_duplicates,
        "exact_duplicates_removed": exact_duplicates,
        "repeated_sensor_id_rows": repeated_sensor_ids,
        "invalid_sensor_ids": int(invalid_sensor_id.sum())
        + numeric_failures.get("sensor_id", 0),
        "invalid_installation_dates": invalid_dates,
        "missing_installation_dates": missing_dates,
        "coordinate_issues": coordinate_issues,
        "missing_values": missing_values,
        "known_sensor_ids": {
            int(value) for value in valid_sensor_ids.dropna().unique()
        },
    }
    return locations, stats


def clean_pedestrian_preview(
    path: Path,
    destination: Path,
    max_rows: int,
    chunk_size: int,
    known_sensor_ids: set[int],
    progress: TextIO,
) -> dict[str, object]:
    reader = pd.read_csv(
        path,
        chunksize=chunk_size,
        dtype="string",
        encoding="utf-8-sig",
    )
    source_columns: list[str] | None = None
    missing_values: dict[str, int] = {}
    numeric_failures: dict[str, int] = {}
    processed_rows = 0
    retained_rows = 0
    removed_invalid_count = 0
    removed_invalid_date = 0
    removed_invalid_sensor_id = 0
    removed_duplicates = 0
    invalid_negative_counts = 0
    invalid_datetime_values = 0
    missing_datetime_values = 0
    invalid_sensor_ids = 0
    missing_sensor_ids = 0
    unmatched_sensor_ids: set[int] = set()
    unmatched_sensor_rows = 0
    time_out_of_range = 0
    logical_key_conflicts = 0
    datetime_min: pd.Timestamp | None = None
    datetime_max: pd.Timestamp | None = None
    seen_records: set[tuple[str, ...]] = set()
    seen_logical_keys: dict[tuple[int, str], tuple[str, ...]] = {}
    header_written = False
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8", newline="") as output:
        while processed_rows < max_rows:
            raw_chunk = next(reader, None)
            if raw_chunk is None:
                break
            remaining = max_rows - processed_rows
            chunk = raw_chunk.iloc[:remaining].copy()
            processed_rows += len(chunk)
            chunk = normalize_text_values(standardize_column_names(chunk))
            if source_columns is None:
                source_columns = list(chunk.columns)
                require_columns(
                    chunk,
                    {
                        "sensor_id",
                        "date_time",
                        "time",
                        "hourly_counts",
                    },
                    "Pedestrian counting dataset",
                )
                missing_values = {column: 0 for column in source_columns}
                numeric_failures = {
                    column: 0 for column in INTEGER_COLUMNS & set(chunk.columns)
                }

            for column in source_columns:
                missing_values[column] += int(chunk[column].isna().sum())

            sensor_source = chunk["sensor_id"].copy()
            count_source = chunk["hourly_counts"].copy()
            date_source = chunk["date_time"].copy()
            chunk, failures = convert_numeric_columns(chunk, INTEGER_COLUMNS)
            for column, count in failures.items():
                numeric_failures[column] = numeric_failures.get(column, 0) + count

            parsed_dates, invalid_dates, missing_dates = parse_datetime_column(
                chunk, "date_time"
            )
            invalid_date_rows = date_source.notna() & parsed_dates.isna()
            chunk["date_time"] = parsed_dates
            invalid_datetime_values += invalid_dates
            missing_datetime_values += missing_dates
            if parsed_dates.notna().any():
                chunk_min = parsed_dates.min()
                chunk_max = parsed_dates.max()
                datetime_min = (
                    chunk_min
                    if datetime_min is None
                    else min(datetime_min, chunk_min)
                )
                datetime_max = (
                    chunk_max
                    if datetime_max is None
                    else max(datetime_max, chunk_max)
                )

            sensor_values = chunk["sensor_id"]
            sensor_parse_failure = sensor_source.notna() & sensor_values.isna()
            sensor_nonpositive = sensor_values.notna() & sensor_values.le(0)
            sensor_fractional = sensor_values.notna() & (
                sensor_values.astype("Float64") % 1
            ).ne(0)
            sensor_invalid = (
                sensor_parse_failure | sensor_nonpositive | sensor_fractional
            ).fillna(False)
            invalid_sensor_ids += int(sensor_invalid.sum())
            missing_sensor_ids += int(sensor_values.isna().sum())
            valid_sensor = sensor_values.notna() & ~sensor_invalid
            for value in sensor_values[valid_sensor].dropna().unique():
                sensor_id = int(value)
                if sensor_id not in known_sensor_ids:
                    unmatched_sensor_ids.add(sensor_id)
            unmatched_mask = valid_sensor & ~sensor_values.isin(known_sensor_ids)
            unmatched_sensor_rows += int(unmatched_mask.sum())

            counts = chunk["hourly_counts"]
            negative_counts = counts.notna() & counts.lt(0)
            invalid_negative_counts += int(negative_counts.sum())
            bad_count_rows = negative_counts | (
                count_source.notna() & counts.isna()
            )
            invalid_sensor_rows = sensor_invalid.copy()
            removed_invalid_count += int(bad_count_rows.sum())
            removed_invalid_date += int(
                (invalid_date_rows & ~bad_count_rows).sum()
            )
            removed_invalid_sensor_id += int(
                (
                    invalid_sensor_rows
                    & ~bad_count_rows
                    & ~invalid_date_rows
                ).sum()
            )

            valid_time = chunk["time"].dropna()
            time_out_of_range += int((~valid_time.between(0, 23)).sum())

            drop_mask = bad_count_rows | invalid_date_rows | invalid_sensor_rows
            chunk = chunk.loc[~drop_mask].copy()
            chunk = chunk.reset_index(drop=True)
            fingerprint_columns = [
                column for column in chunk.columns if column != "id"
            ]
            keep_rows = []
            for row in chunk.itertuples(index=False, name=None):
                values = dict(zip(chunk.columns, row))
                sensor_id = values["sensor_id"]
                timestamp = values["date_time"]
                fingerprint = tuple(
                    "<NA>" if pd.isna(values[column]) else str(values[column])
                    for column in fingerprint_columns
                )
                duplicate = False
                if pd.notna(sensor_id) and pd.notna(timestamp):
                    logical_key = (int(sensor_id), str(timestamp))
                    previous = seen_logical_keys.get(logical_key)
                    if previous is not None and previous != fingerprint:
                        logical_key_conflicts += 1
                    seen_logical_keys.setdefault(logical_key, fingerprint)
                    if fingerprint in seen_records:
                        duplicate = True
                    else:
                        seen_records.add(fingerprint)
                keep_rows.append(not duplicate)

            duplicate_count = keep_rows.count(False)
            removed_duplicates += duplicate_count
            chunk = chunk.loc[keep_rows]
            chunk.to_csv(
                output,
                index=False,
                header=not header_written,
                date_format="%Y-%m-%d %H:%M:%S",
            )
            header_written = True
            retained_rows += len(chunk)
            print(
                f"Pedestrian rows processed: {processed_rows:,}/{max_rows:,}; "
                f"retained: {retained_rows:,}",
                file=progress,
                flush=True,
            )

    if source_columns is None:
        raise ValueError(f"No data rows found in pedestrian dataset: {path}")
    return {
        "processed_rows": processed_rows,
        "retained_rows": retained_rows,
        "removed_rows": processed_rows - retained_rows,
        "removed_invalid_count_rows": removed_invalid_count,
        "removed_invalid_date_rows": removed_invalid_date,
        "removed_invalid_sensor_id_rows": removed_invalid_sensor_id,
        "removed_duplicate_rows": removed_duplicates,
        "invalid_negative_counts": invalid_negative_counts,
        "invalid_datetime_values": invalid_datetime_values,
        "missing_datetime_values": missing_datetime_values,
        "invalid_sensor_ids": invalid_sensor_ids,
        "missing_sensor_ids": missing_sensor_ids,
        "unmatched_sensor_ids": sorted(unmatched_sensor_ids),
        "unmatched_sensor_rows": unmatched_sensor_rows,
        "time_out_of_range": time_out_of_range,
        "logical_key_conflicts": logical_key_conflicts,
        "numeric_failures": numeric_failures,
        "missing_values": missing_values,
        "datetime_min": datetime_min,
        "datetime_max": datetime_max,
    }


def format_counts(counts: dict[str, int]) -> list[str]:
    return [
        f"  - {column}: {count:,}"
        for column, count in counts.items()
    ]


def build_report(
    hourly_path: Path,
    locations_path: Path,
    pedestrian: dict[str, object],
    locations: dict[str, object],
    pedestrian_output: Path,
    locations_output: Path,
    pedestrian_output_size: int,
    locations_output_size: int,
    max_rows: int,
    chunk_size: int,
) -> str:
    coordinate_issues = locations["coordinate_issues"]
    lines = [
        "GeoPulse - Hyper-Local Retail Mobility Analytics",
        "Day 3 Data Cleaning and Quality Validation Report",
        "=" * 58,
        f"Execution time: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "1. Original dataset information",
        f"Pedestrian CSV: data/raw/{HOURLY_FILENAME}",
        f"  - File size: {hourly_path.stat().st_size:,} bytes",
        "  - Original rows: 4,511,349 (as counted in the Day 2 exploration report)",
        f"  - Rows processed this run: {pedestrian['processed_rows']:,} "
        f"(limit {max_rows:,}; chunk size {chunk_size:,})",
        f"Sensor locations CSV: data/raw/{LOCATIONS_FILENAME}",
        f"  - File size: {locations_path.stat().st_size:,} bytes",
        f"  - Original rows: {locations['original_rows']:,}",
        "",
        "2. Cleaning operations performed",
        "  - Standardized column names to lowercase snake_case.",
        "  - Trimmed text values; standardized month/day/direction and status labels.",
        "  - Converted pedestrian numeric fields and parsed date_time values.",
        "  - Converted sensor installation dates, IDs, and coordinates.",
        "  - Validated pedestrian counts, timestamps, sensor IDs, and coordinate ranges.",
        "  - Left missing values unfilled; retained incomplete rows unless a value "
        "was required to establish a clearly invalid record.",
        "  - Removed confirmed duplicate pedestrian records within the processed "
        "preview and exact duplicate sensor-location rows.",
        "",
        "3. Missing values",
        "Pedestrian dataset (processed rows only):",
    ]
    lines.extend(format_counts(pedestrian["missing_values"]))
    lines.append("Sensor location dataset (after exact duplicate removal):")
    lines.extend(format_counts(locations["missing_values"]))

    lines.extend(
        [
            "",
            "4. Invalid values identified",
            f"Pedestrian non-numeric values coerced to missing by column: "
            f"{pedestrian['numeric_failures']}",
            f"  - Negative pedestrian counts: "
            f"{pedestrian['invalid_negative_counts']:,}",
            f"  - Unparseable non-missing date_time values: "
            f"{pedestrian['invalid_datetime_values']:,}",
            f"  - Invalid non-missing sensor IDs (non-numeric, non-positive, "
            f"or non-integer): {pedestrian['invalid_sensor_ids']:,}",
            f"  - Time values outside 0-23: {pedestrian['time_out_of_range']:,}",
            f"  - Valid positive sensor IDs not listed in location metadata "
            f"(rows): {pedestrian['unmatched_sensor_rows']:,}",
            f"Sensor-location invalid sensor IDs: {locations['invalid_sensor_ids']:,}",
            f"  - Unparseable installation dates: "
            f"{locations['invalid_installation_dates']:,}",
        ]
    )
    lines.extend(
        f"  - {name}: {count:,}"
        for name, count in coordinate_issues.items()
    )
    lines.extend(
        [
            "",
            "5. Duplicate handling",
            "Pedestrian records were compared by all standardized fields except "
            "the row ID; matching records with valid sensor_id/date_time were "
            "removed after their first occurrence.",
            f"  - Confirmed pedestrian duplicate rows removed: "
            f"{pedestrian['removed_duplicate_rows']:,}",
            f"  - Repeated sensor/date_time keys with differing row values retained "
            f"as conflicts: {pedestrian['logical_key_conflicts']:,}",
            "Sensor-location exact duplicate rows were removed; repeated sensor IDs "
            "with differing details were retained.",
            f"  - Exact sensor-location duplicates removed: "
            f"{locations['exact_duplicates_removed']:,}",
            f"  - Repeated sensor-ID rows remaining: "
            f"{locations['repeated_sensor_id_rows']:,}",
            "",
            "6. Rows processed, retained, and removed",
            f"Pedestrian: {pedestrian['processed_rows']:,} processed; "
            f"{pedestrian['retained_rows']:,} retained; "
            f"{pedestrian['removed_rows']:,} removed.",
            f"  - Removed for invalid count: "
            f"{pedestrian['removed_invalid_count_rows']:,}",
            f"  - Removed for unparseable non-missing date_time: "
            f"{pedestrian['removed_invalid_date_rows']:,}",
            f"  - Removed for invalid non-missing sensor_id: "
            f"{pedestrian['removed_invalid_sensor_id_rows']:,}",
            f"  - Removed as confirmed duplicates: "
            f"{pedestrian['removed_duplicate_rows']:,}",
            f"Sensor locations: {locations['original_rows']:,} original; "
            f"{locations['retained_rows']:,} retained; "
            f"{locations['removed_rows']:,} removed.",
            "",
            "7. Final output information",
            f"Pedestrian preview: {pedestrian_output.relative_to(ROOT)}",
            f"  - Rows: {pedestrian['retained_rows']:,}; "
            f"columns: {len(pedestrian['missing_values']):,}; "
            f"size: {pedestrian_output_size:,} bytes",
            f"Sensor locations: {locations_output.relative_to(ROOT)}",
            f"  - Rows: {locations['retained_rows']:,}; "
            f"columns: {len(locations['missing_values']):,}; "
            f"size: {locations_output_size:,} bytes",
            f"Parsed pedestrian date range in processed rows: "
            f"{pedestrian['datetime_min']} to {pedestrian['datetime_max']}",
            "",
            "8. Remaining data quality issues",
            f"  - Missing pedestrian date_time values retained: "
            f"{pedestrian['missing_datetime_values']:,}.",
            f"  - Missing pedestrian sensor_id values retained: "
            f"{pedestrian['missing_sensor_ids']:,}.",
            f"  - Missing pedestrian hourly_counts values retained: "
            f"{pedestrian['missing_values'].get('hourly_counts', 0):,}.",
            f"  - Sensor IDs not found in the location file retained and flagged: "
            f"{len(pedestrian['unmatched_sensor_ids']):,} distinct IDs "
            f"{pedestrian['unmatched_sensor_ids']}.",
            "  - Invalid/missing sensor coordinates are retained as missing "
            "coordinate values; their source rows were not removed.",
            "  - Pedestrian quality statistics apply only to the processed preview; "
            "no full-dataset duplicate scan was run.",
            "Raw CSV files were read-only and were not modified.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean sensor metadata and a bounded pedestrian CSV preview."
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=DEFAULT_MAX_ROWS,
        help=(
            f"Maximum pedestrian rows to process (default: {DEFAULT_MAX_ROWS:,}). "
            "Increase this value to process a larger preview."
        ),
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Pandas chunk size (default: {DEFAULT_CHUNK_SIZE:,}).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing Day 3 output files after explicit confirmation by flag.",
    )
    args = parser.parse_args()
    if args.max_rows <= 0:
        parser.error("--max-rows must be greater than zero.")
    if args.chunk_size <= 0:
        parser.error("--chunk-size must be greater than zero.")
    return args


def main() -> int:
    args = parse_args()
    hourly_path = RAW_DIR / HOURLY_FILENAME
    locations_path = RAW_DIR / LOCATIONS_FILENAME
    pedestrian_output = PROCESSED_DIR / "pedestrian_counts_cleaned_preview.csv"
    locations_output = PROCESSED_DIR / "sensor_locations_cleaned.csv"
    report_output = REPORT_PATH
    output_paths = (pedestrian_output, locations_output, report_output)
    temporary_paths = tuple(
        path.with_name(path.name + ".tmp") for path in output_paths
    )

    try:
        for path in (hourly_path, locations_path):
            if not path.is_file():
                raise FileNotFoundError(f"Required dataset not found: {path}")
        if not args.overwrite:
            existing = [str(path) for path in output_paths if path.exists()]
            if existing:
                raise FileExistsError(
                    "Output files already exist; inspect them or rerun with "
                    f"--overwrite: {', '.join(existing)}"
                )
        print("Cleaning sensor-location data...")
        locations_frame, location_stats = clean_sensor_locations(locations_path)
        print(
            f"Sensor locations read: {location_stats['original_rows']:,}; "
            f"retained: {location_stats['retained_rows']:,}."
        )

        print(
            f"Cleaning at most {args.max_rows:,} pedestrian rows "
            f"in chunks of {args.chunk_size:,}..."
        )
        pedestrian_stats = clean_pedestrian_preview(
            hourly_path,
            temporary_paths[0],
            args.max_rows,
            args.chunk_size,
            location_stats["known_sensor_ids"],
            sys.stdout,
        )
        locations_frame.to_csv(temporary_paths[1], index=False, date_format="%Y-%m-%d")
        temporary_paths[2].parent.mkdir(parents=True, exist_ok=True)
        report = build_report(
            hourly_path,
            locations_path,
            pedestrian_stats,
            location_stats,
            pedestrian_output,
            locations_output,
            temporary_paths[0].stat().st_size,
            temporary_paths[1].stat().st_size,
            args.max_rows,
            args.chunk_size,
        )
        temporary_paths[2].write_text(report, encoding="utf-8")
        for temporary, output in zip(temporary_paths, output_paths):
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary.replace(output)
        print(f"Pedestrian preview created: {pedestrian_output.relative_to(ROOT)}")
        print(f"Sensor locations created: {locations_output.relative_to(ROOT)}")
        print(f"Cleaning report created: {report_output.relative_to(ROOT)}")
        return 0
    except (
        OSError,
        ValueError,
        UnicodeError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
    ) as error:
        print(f"Data cleaning failed: {error}", file=sys.stderr)
        return 1
    finally:
        for path in temporary_paths:
            if path.exists():
                path.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
