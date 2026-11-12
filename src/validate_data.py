import csv
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

HOURLY_FILE = (
    ROOT / "data" / "raw"
    / "Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv"
)

LOCATIONS_FILE = (
    ROOT / "data" / "raw"
    / "Pedestrian_Counting_System_-_Sensor_Locations.csv"
)

REPORT_FILE = ROOT / "reports" / "data_quality_report.md"

HOURLY_COLUMNS = [
    "ID", "Date_Time", "Year", "Month", "Mdate",
    "Day", "Time", "Sensor_ID", "Sensor_Name",
    "Hourly_Counts",
]

LOCATION_COLUMNS = [
    "sensor_id", "sensor_description", "sensor_name",
    "installation_date", "status", "note",
    "direction_1", "direction_2", "latitude",
    "longitude", "location",
]

INTEGER_COLUMNS = [
    "ID", "Year", "Mdate", "Time",
    "Sensor_ID", "Hourly_Counts",
]


def check_file(path):
    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")


def read_headers(path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        return next(reader, [])


def validate_hourly_data():
    missing = Counter()
    invalid_integers = Counter()
    sensor_ids = set()
    row_count = 0
    negative_counts = 0
    invalid_dates = 0
    min_date = None
    max_date = None
    total_pedestrians = 0

    with HOURLY_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != HOURLY_COLUMNS:
            raise ValueError(
                f"Unexpected hourly CSV headers: {reader.fieldnames}"
            )

        for row in reader:
            row_count += 1

            for column in HOURLY_COLUMNS:
                if not (row.get(column) or "").strip():
                    missing[column] += 1

            for column in INTEGER_COLUMNS:
                value = (row.get(column) or "").strip()
                if value:
                    try:
                        number = int(value)
                        if column == "Hourly_Counts":
                            total_pedestrians += number
                            if number < 0:
                                negative_counts += 1
                    except ValueError:
                        invalid_integers[column] += 1

            sensor_id = (row.get("Sensor_ID") or "").strip()
            if sensor_id:
                sensor_ids.add(sensor_id)

            date_value = (row.get("Date_Time") or "").strip()
            if date_value:
                try:
                    parsed = datetime.strptime(
                        date_value, "%B %d, %Y %I:%M:%S %p"
                    )
                    min_date = (
                        parsed if min_date is None
                        else min(min_date, parsed)
                    )
                    max_date = (
                        parsed if max_date is None
                        else max(max_date, parsed)
                    )
                except ValueError:
                    invalid_dates += 1

    return {
        "rows": row_count,
        "missing": missing,
        "invalid_integers": invalid_integers,
        "sensor_ids": sensor_ids,
        "negative_counts": negative_counts,
        "invalid_dates": invalid_dates,
        "min_date": min_date,
        "max_date": max_date,
        "total_pedestrians": total_pedestrians,
    }


def validate_locations():
    missing = Counter()
    sensor_ids = set()
    duplicate_ids = set()
    invalid_latitudes = 0
    invalid_longitudes = 0
    invalid_installation_dates = 0
    status_counts = Counter()
    row_count = 0

    with LOCATIONS_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != LOCATION_COLUMNS:
            raise ValueError(
                f"Unexpected location CSV headers: {reader.fieldnames}"
            )

        for row in reader:
            row_count += 1

            for column in LOCATION_COLUMNS:
                if not (row.get(column) or "").strip():
                    missing[column] += 1

            sensor_id = (row.get("sensor_id") or "").strip()
            if sensor_id:
                if sensor_id in sensor_ids:
                    duplicate_ids.add(sensor_id)
                sensor_ids.add(sensor_id)

            status = (row.get("status") or "").strip()
            if status:
                status_counts[status] += 1

            latitude = (row.get("latitude") or "").strip()
            if latitude:
                try:
                    value = float(latitude)
                    if not -90 <= value <= 90:
                        invalid_latitudes += 1
                except ValueError:
                    invalid_latitudes += 1

            longitude = (row.get("longitude") or "").strip()
            if longitude:
                try:
                    value = float(longitude)
                    if not -180 <= value <= 180:
                        invalid_longitudes += 1
                except ValueError:
                    invalid_longitudes += 1

            installation_date = (
                row.get("installation_date") or ""
            ).strip()

            if installation_date:
                try:
                    datetime.strptime(
                        installation_date, "%Y/%m/%d"
                    )
                except ValueError:
                    invalid_installation_dates += 1

    return {
        "rows": row_count,
        "missing": missing,
        "sensor_ids": sensor_ids,
        "duplicate_ids": duplicate_ids,
        "invalid_latitudes": invalid_latitudes,
        "invalid_longitudes": invalid_longitudes,
        "invalid_installation_dates": invalid_installation_dates,
        "status_counts": status_counts,
    }


def markdown_table(counter, value_label):
    lines = [f"| Column | {value_label} |", "|---|---:|"]

    for column in sorted(counter):
        lines.append(f"| `{column}` | {counter[column]} |")

    return "\n".join(lines)


def generate_report(hourly, locations):
    unmatched_hourly = (
        hourly["sensor_ids"] - locations["sensor_ids"]
    )
    unused_locations = (
        locations["sensor_ids"] - hourly["sensor_ids"]
    )

    lines = [
        "# GeoPulse – Data Quality Report",
        "",
        "## 1. Hourly Pedestrian Counts",
        "",
        f"- Total records: **{hourly['rows']:,}**",
        f"- Unique sensor IDs: **{len(hourly['sensor_ids']):,}**",
        f"- Total recorded pedestrian passages: "
        f"**{hourly['total_pedestrians']:,}**",
        f"- Earliest observation: **{hourly['min_date']}**",
        f"- Latest observation: **{hourly['max_date']}**",
        f"- Invalid date values: **{hourly['invalid_dates']:,}**",
        f"- Negative pedestrian counts: "
        f"**{hourly['negative_counts']:,}**",
        "",
        "### Missing Values",
        "",
        markdown_table(hourly["missing"], "Missing values"),
        "",
        "### Invalid Integer Values",
        "",
        markdown_table(hourly["invalid_integers"], "Invalid values"),
        "",
        "## 2. Sensor Locations",
        "",
        f"- Total location records: **{locations['rows']:,}**",
        f"- Unique sensor IDs: **{len(locations['sensor_ids']):,}**",
        f"- Duplicate sensor IDs: "
        f"**{len(locations['duplicate_ids']):,}**",
        f"- Invalid latitude values: "
        f"**{locations['invalid_latitudes']:,}**",
        f"- Invalid longitude values: "
        f"**{locations['invalid_longitudes']:,}**",
        f"- Invalid installation dates: "
        f"**{locations['invalid_installation_dates']:,}**",
        "",
        "### Missing Values",
        "",
        markdown_table(locations["missing"], "Missing values"),
        "",
        "### Recorded Sensor Status Values",
        "",
        "| Status | Records |",
        "|---|---:|",
    ]

    for status, count in sorted(locations["status_counts"].items()):
        lines.append(f"| `{status}` | {count} |")

    lines.extend([
        "",
        "## 3. Sensor ID Matching",
        "",
        f"- Hourly sensor IDs without location records: "
        f"**{len(unmatched_hourly):,}**",
        f"- Location sensor IDs without hourly records: "
        f"**{len(unused_locations):,}**",
    ])

    if unmatched_hourly:
        lines.append(
            "- Unmatched hourly sensor IDs: "
            + ", ".join(sorted(unmatched_hourly))
        )

    if unused_locations:
        lines.append(
            "- Location-only sensor IDs: "
            + ", ".join(sorted(unused_locations))
        )

    lines.extend([
        "",
        "## 4. Interpretation",
        "",
        "These checks describe structural and basic value quality. "
        "They do not establish that every observation is accurate "
        "or that a sensor was operational throughout its recorded period.",
        "",
        "Pedestrian counts represent sensor-recorded passages, "
        "not verified unique people, purchases, or retail revenue.",
        "",
        "## 5. Validation Scope",
        "",
        "This report was generated by `src/validate_data.py`. "
        "The raw source files were read without modifying them.",
        "",
    ])

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    check_file(HOURLY_FILE)
    check_file(LOCATIONS_FILE)

    print("Validating hourly pedestrian counts...")
    hourly = validate_hourly_data()

    print("Validating sensor locations...")
    locations = validate_locations()

    generate_report(hourly, locations)

    print("\nValidation completed.")
    print(f"Hourly records: {hourly['rows']:,}")
    print(f"Location records: {locations['rows']:,}")
    print(f"Hourly unique sensors: {len(hourly['sensor_ids']):,}")
    print(f"Location unique sensors: {len(locations['sensor_ids']):,}")
    print(f"Report created: {REPORT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
