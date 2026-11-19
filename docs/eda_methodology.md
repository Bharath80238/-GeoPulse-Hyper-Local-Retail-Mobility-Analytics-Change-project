\# GeoPulse - Exploratory Data Analysis Methodology
\## 1. Objective
This analysis explores Melbourne's hourly pedestrian-counting data to identify temporal patterns, compare recorded activity across sensors, and provide location-level information that may support retail mobility and planning decisions.
The analysis uses only the two supplied CSV datasets.
\## 2. Source Datasets
\### Hourly Pedestrian Counts
File: `Pedestrian\_Counting\_System\_-\_Monthly\_\_counts\_per\_hour\_.csv`
Contains hourly pedestrian-count records, including:
\- Date and time
\- Sensor ID and sensor name
\- Hourly pedestrian count
\### Sensor Locations
File: `Pedestrian\_Counting\_System\_-\_Sensor\_Locations.csv`
Contains sensor metadata, including:
\- Sensor ID and description
\- Installation date and status
\- Latitude and longitude
\- Location information
The datasets are joined using hourly `Sensor\_ID` and location `sensor\_id`.

\## 3. Processing Approach
The hourly CSV is large, so the analysis uses pandas chunk-based processing.
\- Chunk size: 250,000 rows.
\- Only the required columns are loaded.
\- Each chunk's timestamp is parsed using the source date format.
\- Date, hour, year, and year-month fields are derived.
\- Aggregations are calculated within each chunk.
\- Partial aggregation results are combined to produce final outputs.
This reduces memory usage compared with loading the complete hourly dataset into memory.
The raw source CSV files are not modified.

\## 4. Analysis and Metric Definitions
\### Daily Analysis
Groups records by calendar date.
\- `Pedestrian\_Passages`: Sum of hourly counts across available sensor records for that date.
\- `Sensor\_Hour\_Records`: Number of sensor-hour records contributing to the daily total.
\- `Day`: Weekday name derived from the date.
\- `Day\_Type`: Weekday or weekend classification.
\### Hourly Analysis
Groups records by hour of the day, from 00:00 to 23:00.
\- `Pedestrian\_Passages`: Combined count across all available sensor records for that hour.
\- `Sensor\_Hour\_Records`: Number of records contributing to the hourly total.
\- `Average\_Passages\_Per\_Sensor\_Record`: Total passages divided by the number of contributing records.
The busiest hour is the hour with the highest combined recorded count across sensors.
\### Weekday Patterns
Calculates the average and median daily pedestrian passages for each weekday, along with the number of recorded dates.
\### Weekday and Weekend Comparison
Groups daily totals into weekdays and weekends.
\- `Average\_Daily\_Passages`: Mean of daily totals for the corresponding day type.
\- `Median\_Daily\_Passages`: Median of daily totals.
\- `Number\_Of\_Days`: Number of dates represented in the dataset.
This compares average daily totals rather than raw totals across unequal numbers of weekdays and weekend days.
\### Monthly and Yearly Trends
Groups records by year-month and year.
For each period, the analysis calculates:
\- Total recorded pedestrian passages.
\- Number of contributing sensor-hour records.
\### Sensor Rankings
Groups records by sensor ID and calculates:
\- `Pedestrian\_Passages`: Total recorded passages for the sensor.
\- `Sensor\_Hour\_Records`: Number of recorded sensor-hour rows.
\- `Average\_Hourly\_Passages`: Total passages divided by recorded sensor-hour rows.
Sensor metadata is then joined using sensor ID. The resulting table includes location, status, latitude, and longitude.
Rankings are sorted by total recorded passages in descending order.

\## 5. Generated Outputs
All outputs are written to `reports/eda/`.
| File | Description |
|---|---|
| `daily\_totals.csv` | Daily passage totals and date classifications |
| `hourly\_patterns.csv` | Hour-of-day totals and average per sensor record |
| `weekday\_patterns.csv` | Average and median daily passages by weekday |
| `weekday\_weekend.csv` | Average and median daily totals by day type |
| `monthly\_trends.csv` | Monthly passage totals |
| `yearly\_trends.csv` | Yearly passage totals |
| `sensor\_rankings.csv` | Sensor-level totals, averages, and location metadata |
| `eda\_report.md` | Summary of key findings and limitations |

\## 6. Validation Approach

The generated outputs are checked to ensure that their total passage counts reconcile with the overall source total.
The daily, hourly, monthly, yearly, and sensor-level aggregate totals should each equal the total pedestrian passages processed from the source data.
The sensor-level output is also checked for expected sensor coverage and available location coordinates.
Automated tests cover chunk aggregation and an end-to-end analysis using a small controlled dataset.

\## 7. Interpretation and Limitations
\- Counts represent sensor-recorded pedestrian passages, not verified unique individuals.
\- They cannot directly establish retail customers, store visits, purchases, sales, or revenue.
\- Sensor totals depend on installation dates, operating periods, observation availability, and physical coverage.
\- Average passages per recorded sensor-hour are not a complete sensor-uptime adjustment.
\- The busiest hour across all sensors does not necessarily represent the busiest hour at every individual sensor.
\- Daily averages are calculated over dates represented in the dataset; dates with no records are not automatically treated as zero.
\- Historical trends may reflect changes in sensor coverage and operating conditions as well as changes in pedestrian activity.
\- The analysis is descriptive and does not establish causal relationships.

8\. Reproducibility
Run the analysis from the project root:
python .\\src\\eda.py
Run the automated tests:
python -m pytest -v
The source datasets must be available in data/raw/ with their expected filenames.
