# GeoPulse – Dataset Inventory
## 1. Project Data Sources
This project uses two CSV datasets from the uploaded pedestrian counting
system archive. Both datasets describe pedestrian movement in Melbourne,
Australia.
### Dataset 1: Hourly Pedestrian Counts
**File:** `Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv`
**Purpose:** Records hourly pedestrian counts captured by sensors at
different locations.
**Columns:**
- `ID`: Record identifier.
- `Date_Time`: Date and time of the hourly observation.
- `Year`: Calendar year.
- `Month`: Month name.
- `Mdate`: Day of the month.
- `Day`: Day of the week.
- `Time`: Hour of the day.
- `Sensor_ID`: Identifier of the pedestrian counting sensor.
- `Sensor_Name`: Name of the sensor location.
- `Hourly_Counts`: Recorded pedestrian count for that hour.
### Dataset 2: Sensor Locations
**File:** `Pedestrian_Counting_System_-_Sensor_Locations.csv`
**Purpose:** Provides geographical and descriptive information about
pedestrian counting sensors.
**Columns:**
- `sensor_id`: Sensor identifier.
- `sensor_description`: Description of the sensor location.
- `sensor_name`: Sensor name.
- `installation_date`: Sensor installation date.
- `status`: Recorded sensor status.
- `note`: Additional information about the sensor.
- `direction_1`: First recorded movement direction.
- `direction_2`: Second recorded movement direction.
- `latitude`: Geographic latitude.
- `longitude`: Geographic longitude.
- `location`: Coordinate representation.
## 2. Relationship Between Datasets
The datasets can be connected using the sensor identifier:
`Hourly_Counts.Sensor_ID = Sensor_Locations.sensor_id`
This relationship allows hourly pedestrian activity to be analyzed
alongside sensor location information.
## 3. Planned Analytical Scope
The project will investigate:
- Overall pedestrian footfall patterns.
- Busiest sensor locations.
- Peak pedestrian activity hours.
- Weekday and weekend patterns.
- Monthly and yearly trends.
- Differences between sensor locations.
- Geographic distribution of pedestrian activity.
- Sensor metadata and data quality.
## 4. Data Handling Rules
- Original datasets are retained in `data/raw/`.
- Raw datasets are excluded from Git using `.gitignore`.
- Data validation and cleaning will be performed before analysis.
- Processed datasets and analytical outputs will be stored separately.
- Missing, invalid, and unmatched records will be documented.
## 5. Important Limitations
Pedestrian counts represent recorded sensor passages. They do not
necessarily represent unique individuals, retail customers, shop visits,
purchases, or revenue.
The project can support retail mobility and location-planning insights,
but it cannot directly measure retail sales or customer conversion.
Sensor status values and other metadata will be interpreted only after
their definitions and data quality have been examined.
## 6. Validation Status
Initial CSV headers have been inspected. Full dataset profiling,
date-range verification, missing-value checks, sensor matching, and
numeric validation are pending.