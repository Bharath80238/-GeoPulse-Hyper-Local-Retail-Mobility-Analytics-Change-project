# GeoPulse - Exploratory Data Analysis

## 1. Dataset Overview

- Hourly records analyzed: **4,511,349**
- Recorded pedestrian passages: **2,227,952,977**
- Unique sensors: **82**
- First observation: **2009-05-01 00:00:00**
- Last observation: **2022-09-30 23:00:00**

## 2. Key Findings

- Busiest recorded date: **2019-08-23** (1,149,216 passages)
- Busiest hour across all sensors: **17:00**
- Busiest sensor by total recorded passages: **Town Hall (West)** (145,343,894)
- Lowest-total sensor: **Errol St (West)** (238,586)

## 3. Output Files

- `daily_totals.csv`
- `hourly_patterns.csv`
- `weekday_patterns.csv`
- `weekday_weekend.csv`
- `monthly_trends.csv`
- `yearly_trends.csv`
- `sensor_rankings.csv`

## 4. Interpretation and Limitations

The analysis summarizes sensor-recorded pedestrian passages. These are not verified unique people, retail customers, store visits, purchases, or revenue.

Sensor totals can be affected by installation dates, operating periods, missing observations, and sensor coverage. Comparisons should therefore be interpreted with these limitations in mind.

Hourly patterns represent aggregated sensor-hour records. Weekday and weekend comparisons use average daily totals, rather than comparing totals across unequal numbers of days.

The raw source datasets were not modified.
