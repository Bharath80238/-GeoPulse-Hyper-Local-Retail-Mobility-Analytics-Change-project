
import pandas as pd

from src import eda


def test_combine_aggregates():
    frames = [
        pd.DataFrame({
            "Date": ["2019-11-01", "2019-11-02"],
            "Pedestrian_Passages": [10, 20],
            "Sensor_Hour_Records": [1, 1],
        }),
        pd.DataFrame({
            "Date": ["2019-11-01", "2019-11-03"],
            "Pedestrian_Passages": [30, 40],
            "Sensor_Hour_Records": [2, 1],
        }),
    ]

    result = eda.combine_aggregates(
        frames,
        "Date",
        ["Pedestrian_Passages", "Sensor_Hour_Records"],
    )

    first_day = result[result["Date"] == "2019-11-01"].iloc[0]

    assert first_day["Pedestrian_Passages"] == 40
    assert first_day["Sensor_Hour_Records"] == 3
    assert result["Pedestrian_Passages"].sum() == 100


def test_end_to_end_analysis(tmp_path, monkeypatch):
    hourly_file = tmp_path / "hourly.csv"
    locations_file = tmp_path / "locations.csv"
    output_dir = tmp_path / "eda"

    hourly = pd.DataFrame({
        "Date_Time": [
            "November 01, 2019 05:00:00 PM",
            "November 01, 2019 05:00:00 PM",
            "November 02, 2019 06:00:00 PM",
            "November 04, 2019 09:00:00 AM",
        ],
        "Sensor_ID": [1, 2, 1, 2],
        "Sensor_Name": [
            "Sensor One",
            "Sensor Two",
            "Sensor One",
            "Sensor Two",
        ],
        "Hourly_Counts": [10, 20, 30, 40],
    })

    locations = pd.DataFrame({
        "sensor_id": [1, 2],
        "latitude": [-37.81, -37.82],
        "longitude": [144.96, 144.97],
        "location": ["Location One", "Location Two"],
        "status": ["A", "A"],
    })

    hourly.to_csv(hourly_file, index=False)
    locations.to_csv(locations_file, index=False)

    monkeypatch.setattr(eda, "HOURLY_FILE", hourly_file)
    monkeypatch.setattr(eda, "LOCATIONS_FILE", locations_file)
    monkeypatch.setattr(eda, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(eda, "CHUNK_SIZE", 2)

    eda.analyze()

    daily = pd.read_csv(output_dir / "daily_totals.csv")
    hourly_result = pd.read_csv(output_dir / "hourly_patterns.csv")
    weekday_weekend = pd.read_csv(
        output_dir / "weekday_weekend.csv"
    )
    sensors = pd.read_csv(output_dir / "sensor_rankings.csv")
    monthly = pd.read_csv(output_dir / "monthly_trends.csv")
    yearly = pd.read_csv(output_dir / "yearly_trends.csv")

    assert len(daily) == 3
    assert daily["Pedestrian_Passages"].sum() == 100

    assert hourly_result["Pedestrian_Passages"].sum() == 100
    assert monthly["Pedestrian_Passages"].sum() == 100
    assert yearly["Pedestrian_Passages"].sum() == 100

    assert sensors["Sensor_ID"].nunique() == 2
    assert sensors["Pedestrian_Passages"].sum() == 100
    assert sensors.iloc[0]["Sensor_ID"] == 2
    assert sensors.iloc[0]["Pedestrian_Passages"] == 60
    assert sensors["latitude"].notna().all()
    assert sensors["longitude"].notna().all()

    weekday = weekday_weekend.set_index("Day_Type")

    assert weekday.loc["Weekday", "Average_Daily_Passages"] == 35
    assert weekday.loc["Weekend", "Average_Daily_Passages"] == 30

    report = output_dir / "eda_report.md"
    assert report.is_file()
    assert report.read_bytes().startswith(b"\xef\xbb\xbf")
