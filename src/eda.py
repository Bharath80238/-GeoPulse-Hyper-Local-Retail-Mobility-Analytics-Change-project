from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

HOURLY_FILE = (
    ROOT / "data" / "raw"
    / "Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv"
)

LOCATIONS_FILE = (
    ROOT / "data" / "raw"
    / "Pedestrian_Counting_System_-_Sensor_Locations.csv"
)

OUTPUT_DIR = ROOT / "reports" / "eda"

CHUNK_SIZE = 250_000

DATE_FORMAT = "%B %d, %Y %I:%M:%S %p"

USE_COLUMNS = [
    "Date_Time",
    "Sensor_ID",
    "Sensor_Name",
    "Hourly_Counts",
]


def combine_aggregates(frames, group_column, sum_columns):
    """Combine partial groupby results from multiple CSV chunks."""
    combined = pd.concat(frames, ignore_index=True)

    return (
        combined.groupby(group_column, as_index=False)[sum_columns]
        .sum()
    )


def analyze():
    if not HOURLY_FILE.is_file():
        raise FileNotFoundError(f"Hourly dataset not found: {HOURLY_FILE}")

    if not LOCATIONS_FILE.is_file():
        raise FileNotFoundError(f"Sensor locations not found: {LOCATIONS_FILE}")

    daily_parts = []
    hourly_parts = []
    monthly_parts = []
    yearly_parts = []
    sensor_parts = []

    total_rows = 0
    total_passages = 0
    min_date = None
    max_date = None

    print("Starting chunked pedestrian data analysis...")

    reader = pd.read_csv(
        HOURLY_FILE,
        usecols=USE_COLUMNS,
        dtype={
            "Sensor_ID": "int32",
            "Hourly_Counts": "int64",
            "Sensor_Name": "string",
        },
        chunksize=CHUNK_SIZE,
    )

    for chunk_number, chunk in enumerate(reader, start=1):
        chunk["Date_Time"] = pd.to_datetime(
            chunk["Date_Time"],
            format=DATE_FORMAT,
            errors="raise",
        )

        dates = chunk["Date_Time"]

        chunk["Date"] = dates.dt.strftime("%Y-%m-%d")
        chunk["Hour"] = dates.dt.hour
        chunk["Year"] = dates.dt.year
        chunk["Year_Month"] = dates.dt.strftime("%Y-%m")

        total_rows += len(chunk)
        total_passages += int(chunk["Hourly_Counts"].sum())

        chunk_min = dates.min()
        chunk_max = dates.max()

        min_date = chunk_min if min_date is None else min(min_date, chunk_min)
        max_date = chunk_max if max_date is None else max(max_date, chunk_max)

        daily_parts.append(
            chunk.groupby("Date", as_index=False).agg(
                Pedestrian_Passages=("Hourly_Counts", "sum"),
                Sensor_Hour_Records=("Hourly_Counts", "size"),
            )
        )

        hourly_parts.append(
            chunk.groupby("Hour", as_index=False).agg(
                Pedestrian_Passages=("Hourly_Counts", "sum"),
                Sensor_Hour_Records=("Hourly_Counts", "size"),
            )
        )

        monthly_parts.append(
            chunk.groupby("Year_Month", as_index=False).agg(
                Pedestrian_Passages=("Hourly_Counts", "sum"),
                Sensor_Hour_Records=("Hourly_Counts", "size"),
            )
        )

        yearly_parts.append(
            chunk.groupby("Year", as_index=False).agg(
                Pedestrian_Passages=("Hourly_Counts", "sum"),
                Sensor_Hour_Records=("Hourly_Counts", "size"),
            )
        )

        sensor_parts.append(
            chunk.groupby("Sensor_ID", as_index=False).agg(
                Pedestrian_Passages=("Hourly_Counts", "sum"),
                Sensor_Hour_Records=("Hourly_Counts", "size"),
                Average_Hourly_Passages=("Hourly_Counts", "mean"),
                Sensor_Name=("Sensor_Name", "first"),
            )
        )

        print(
            f"Processed chunk {chunk_number:,} "
            f"({total_rows:,} records so far)"
        )

    print("Combining chunk results...")

    daily = combine_aggregates(
        daily_parts,
        "Date",
        ["Pedestrian_Passages", "Sensor_Hour_Records"],
    )

    daily["Date"] = pd.to_datetime(daily["Date"])
    daily["Day"] = daily["Date"].dt.day_name()
    daily["Day_Type"] = daily["Date"].dt.dayofweek.map(
        lambda day: "Weekend" if day >= 5 else "Weekday"
    )
    daily = daily.sort_values("Date")

    hourly = combine_aggregates(
        hourly_parts,
        "Hour",
        ["Pedestrian_Passages", "Sensor_Hour_Records"],
    )
    hourly["Average_Passages_Per_Sensor_Record"] = (
        hourly["Pedestrian_Passages"] / hourly["Sensor_Hour_Records"]
    )
    hourly = hourly.sort_values("Hour")

    monthly = combine_aggregates(
        monthly_parts,
        "Year_Month",
        ["Pedestrian_Passages", "Sensor_Hour_Records"],
    ).sort_values("Year_Month")

    yearly = combine_aggregates(
        yearly_parts,
        "Year",
        ["Pedestrian_Passages", "Sensor_Hour_Records"],
    ).sort_values("Year")

    weekday_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
    ]

    weekday = (
        daily.groupby("Day")
        .agg(
            Average_Daily_Passages=("Pedestrian_Passages", "mean"),
            Median_Daily_Passages=("Pedestrian_Passages", "median"),
            Number_Of_Days=("Date", "count"),
        )
        .reindex(weekday_order)
        .reset_index()
    )

    weekday_weekend = (
        daily.groupby("Day_Type")
        .agg(
            Average_Daily_Passages=("Pedestrian_Passages", "mean"),
            Median_Daily_Passages=("Pedestrian_Passages", "median"),
            Number_Of_Days=("Date", "count"),
        )
        .reset_index()
    )

    sensor = (
        pd.concat(sensor_parts, ignore_index=True)
        .groupby("Sensor_ID", as_index=False)
        .agg(
            Pedestrian_Passages=("Pedestrian_Passages", "sum"),
            Sensor_Hour_Records=("Sensor_Hour_Records", "sum"),
            Sensor_Name=("Sensor_Name", "first"),
        )
    )

    sensor["Average_Hourly_Passages"] = (
        sensor["Pedestrian_Passages"] / sensor["Sensor_Hour_Records"]
    )

    locations = pd.read_csv(LOCATIONS_FILE)
    locations["sensor_id"] = pd.to_numeric(
        locations["sensor_id"], errors="raise"
    ).astype("int32")

    sensor = sensor.merge(
        locations[
            ["sensor_id", "latitude", "longitude", "location", "status"]
        ],
        left_on="Sensor_ID",
        right_on="sensor_id",
        how="left",
        validate="one_to_one",
    ).drop(columns=["sensor_id"])

    sensor = sensor.sort_values(
        "Pedestrian_Passages", ascending=False
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = {
        "daily_totals.csv": daily,
        "hourly_patterns.csv": hourly,
        "weekday_patterns.csv": weekday,
        "weekday_weekend.csv": weekday_weekend,
        "monthly_trends.csv": monthly,
        "yearly_trends.csv": yearly,
        "sensor_rankings.csv": sensor,
    }

    for filename, dataframe in outputs.items():
        dataframe.to_csv(OUTPUT_DIR / filename, index=False)

    generate_report(
        total_rows,
        total_passages,
        min_date,
        max_date,
        daily,
        hourly,
        sensor,
    )

    print("\nEDA completed successfully.")
    print(f"Total records: {total_rows:,}")
    print(f"Total pedestrian passages: {total_passages:,}")
    print(f"Unique sensors: {sensor['Sensor_ID'].nunique():,}")
    print(f"Date range: {min_date} to {max_date}")
    print(f"Output directory: {OUTPUT_DIR}")


def generate_report(
    total_rows,
    total_passages,
    min_date,
    max_date,
    daily,
    hourly,
    sensor,
):
    busiest_day = daily.loc[daily["Pedestrian_Passages"].idxmax()]
    busiest_hour = hourly.loc[hourly["Pedestrian_Passages"].idxmax()]
    busiest_sensor = sensor.iloc[0]
    least_busy_sensor = sensor.iloc[-1]

    lines = [
       "# GeoPulse - Exploratory Data Analysis",
        "",
        "## 1. Dataset Overview",
        "",
        f"- Hourly records analyzed: **{total_rows:,}**",
        f"- Recorded pedestrian passages: **{total_passages:,}**",
        f"- Unique sensors: **{sensor['Sensor_ID'].nunique():,}**",
        f"- First observation: **{min_date}**",
        f"- Last observation: **{max_date}**",
        "",
        "## 2. Key Findings",
        "",
        f"- Busiest recorded date: **{busiest_day['Date'].date()}** "
        f"({int(busiest_day['Pedestrian_Passages']):,} passages)",
        f"- Busiest hour across all sensors: **{int(busiest_hour['Hour']):02d}:00**",
        f"- Busiest sensor by total recorded passages: "
        f"**{busiest_sensor['Sensor_Name']}** "
        f"({int(busiest_sensor['Pedestrian_Passages']):,})",
        f"- Lowest-total sensor: **{least_busy_sensor['Sensor_Name']}** "
        f"({int(least_busy_sensor['Pedestrian_Passages']):,})",
        "",
        "## 3. Output Files",
        "",
        *[f"- `{name}`" for name in [
            "daily_totals.csv",
            "hourly_patterns.csv",
            "weekday_patterns.csv",
            "weekday_weekend.csv",
            "monthly_trends.csv",
            "yearly_trends.csv",
            "sensor_rankings.csv",
        ]],
        "",
        "## 4. Interpretation and Limitations",
        "",
        "The analysis summarizes sensor-recorded pedestrian passages. "
        "These are not verified unique people, retail customers, store visits, "
        "purchases, or revenue.",
        "",
        "Sensor totals can be affected by installation dates, operating "
        "periods, missing observations, and sensor coverage. Comparisons "
        "should therefore be interpreted with these limitations in mind.",
        "",
        "Hourly patterns represent aggregated sensor-hour records. "
        "Weekday and weekend comparisons use average daily totals, "
        "rather than comparing totals across unequal numbers of days.",
        "",
        "The raw source datasets were not modified.",
        "",
    ]

    (OUTPUT_DIR / "eda_report.md").write_text(
        "\n".join(lines),
        encoding="utf-8-sig",
    )


if __name__ == "__main__":
    analyze()
