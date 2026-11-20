# GeoPulse — Analytical Insights Report

## 1. Project Overview

GeoPulse is a hyper-local retail mobility analytics project that analyzes pedestrian movement patterns across Melbourne using historical pedestrian sensor data.

The objective is to identify temporal and location-based pedestrian movement patterns and derive evidence-based insights that may support retail location evaluation, staffing decisions, operating schedules, and planning activities.

The analysis focuses on:
- Pedestrian activity by hour
- Daily and weekly patterns
- Weekday versus weekend movement
- Monthly and yearly trends
- Sensor-level pedestrian activity
- Sensor observation coverage
- Potential retail-planning implications

Pedestrian passages are used as a proxy for observed movement, not as a direct measure of retail customers or sales.

---

## 2. Dataset Overview

The project uses two supplied datasets:

1. Pedestrian counting system hourly counts
2. Pedestrian sensor location metadata

The hourly dataset contains pedestrian passage counts recorded by sensors over time. The sensor metadata dataset provides information about sensor locations, names, coordinates, installation dates, statuses, and other available attributes.

### Dataset summary

| Metric | Value |
|---|---:|
| Hourly records | 4,511,349 |
| Sensor location records | 91 |
| Unique sensors in hourly data | 82 |
| Total recorded pedestrian passages | 2,227,952,977 |
| Start date | 2009-05-01 |
| End date | 2022-09-30 |
| Invalid timestamps | 0 |
| Negative passage counts | 0 |
| Unmatched hourly sensor IDs | 0 |

The hourly dataset contains records from May 2009 through September 2022. The beginning and end of this period are partial calendar years.

---

## 3. Hourly Pedestrian Activity

Hourly analysis reveals a clear variation in pedestrian movement throughout the day.

Recorded activity is lowest during the early morning hours, particularly around 4:00 AM, and increases from approximately 6:00 AM. Activity rises considerably during daytime hours, with strong midday and afternoon movement.

### Key findings

- Highest total passage volume: 5:00 PM
- Passages recorded at 5:00 PM: 207,393,884
- Second-highest hour: 1:00 PM
- Passages recorded at 1:00 PM: 191,648,784
- Lowest hour: 4:00 AM
- Passages recorded at 4:00 AM: 5,142,338

The pedestrian activity pattern indicates strong daytime movement, with significant afternoon activity and a decline during later evening hours.

### Retail-planning implication

The observed pattern may support investigation of staffing requirements, promotional schedules, operating hours, and resource allocation during different time periods.

Retailers may investigate midday and late-afternoon periods as potential high-traffic windows. However, the pedestrian count data alone cannot establish whether these periods generate higher sales or conversion rates.

---

## 4. Weekly Pedestrian Activity

Average daily pedestrian passages differ across the days of the week.

### Key findings

| Day | Average daily passages |
|---|---:|
| Monday | 434,935 |
| Tuesday | 452,029 |
| Wednesday | 470,627 |
| Thursday | 480,480 |
| Friday | 529,373 |
| Saturday | 442,368 |
| Sunday | 372,221 |

Friday recorded the highest average daily passage volume, while Sunday recorded the lowest.

The pattern generally increases from Monday through Friday before declining over the weekend.

Friday's average daily pedestrian passage volume was approximately 42.2% higher than Sunday's.

### Retail-planning implication

The weekly pattern may help retail planners investigate:
- Staffing differences across weekdays
- Friday operational requirements
- Weekend scheduling
- Promotional timing
- Differences in weekday and weekend operating strategies

These findings represent pedestrian movement patterns and should not be treated as direct evidence of retail demand.

---

## 5. Weekday Versus Weekend Comparison

The weekday/weekend comparison provides a broader view of differences in pedestrian movement.

### Key findings

| Metric | Weekdays | Weekends |
|---|---:|---:|
| Number of days | 3,501 | 1,400 |
| Average daily passages | 473,505 | 407,294 |
| Median daily passages | 467,346 | 414,957 |

Weekdays recorded approximately 66,211 more passages per day on average than weekends.

The average weekday passage volume was approximately 16.3% higher than the weekend average.

### Interpretation

The results indicate stronger aggregate pedestrian movement during weekdays across the analyzed sensor network.

The difference may reflect a combination of commuting, business activity, education, transport movement, shopping, tourism, and other reasons for pedestrian movement. The available data does not independently identify these causes.

### Retail-planning implication

Retailers could use this pattern as a basis for investigating weekday staffing, weekend staffing, promotional strategies, and operating requirements.

Individual stores may exhibit patterns different from the citywide aggregate, so local validation would be necessary before applying these findings to a particular retail location.

---

## 6. Monthly Pedestrian Trends

Monthly analysis reveals changes in pedestrian passage volume over the historical period.

Recorded activity generally increased across the earlier years, with substantial pedestrian movement observed during 2019.

A major decline occurred during 2020.

### Illustrative monthly comparison

| Month | Total passages | Sensor-hour records |
|---|---:|---:|
| December 2019 | 24,931,172 | 41,151 |
| January 2020 | 23,189,121 | 41,857 |
| March 2020 | 16,576,373 | 42,984 |
| April 2020 | 3,965,628 | 40,995 |
| August 2020 | 3,157,701 | 42,144 |
| April 2022 | 19,469,918 | 46,850 |

April 2020 recorded approximately 3.97 million passages, compared with approximately 23.19 million in January 2020.

The decline coincides with the COVID-19 pandemic and the associated restrictions and disruption to movement in Melbourne.

The volume of sensor-hour records remained substantial during this period. Therefore, the decline in passage counts was not explained solely by a corresponding decline in the number of records. Changes in sensor coverage, operating periods, and the sensor network should still be considered.

Subsequent periods show recovery in pedestrian activity, although the pattern varies across months.

### Retail-planning implication

The monthly trends demonstrate the importance of considering external disruptions when evaluating pedestrian movement.

Historical pedestrian patterns should not be assumed to remain stable under major social, economic, transport, or environmental changes.

This analysis may help retail planners understand the importance of monitoring mobility trends over time rather than relying exclusively on historical averages.

---

## 7. Yearly Pedestrian Trends

Annual pedestrian passage totals generally increased during the earlier years of the dataset, reaching their highest full-year total in 2019.

### Annual totals

| Year | Pedestrian passages | Sensor-hour records |
|---|---:|---:|
| 2009 | 62,650,110 | 101,400 |
| 2010 | 93,459,437 | 153,288 |
| 2011 | 90,571,965 | 148,752 |
| 2012 | 102,215,521 | 157,465 |
| 2013 | 117,389,820 | 184,725 |
| 2014 | 169,500,386 | 278,318 |
| 2015 | 209,099,687 | 336,770 |
| 2016 | 228,757,880 | 361,087 |
| 2017 | 216,586,414 | 358,132 |
| 2018 | 261,909,318 | 430,072 |
| 2019 | 266,411,675 | 456,829 |
| 2020 | 121,941,994 | 516,100 |
| 2021 | 139,291,234 | 594,855 |
| 2022 | 148,167,536 | 433,556 |

2019 recorded approximately 266.4 million pedestrian passages, the highest annual total among the complete years presented.

However, sensor-hour records increased substantially over time. Therefore, raw passage totals alone should not be used to determine whether pedestrian activity genuinely increased at a comparable rate.

### Normalized passage rate

Passage totals divided by recorded sensor-hour observations provide an additional metric for historical comparison.

| Year | Average passages per sensor-hour |
|---|---:|
| 2015 | 620.90 |
| 2016 | 633.53 |
| 2017 | 604.77 |
| 2018 | 608.99 |
| 2019 | 583.18 |
| 2020 | 236.28 |
| 2021 | 234.16 |
| 2022 | 341.75 |

The normalized passage rate was relatively stable across several pre-2020 years, although variations occurred. A substantial reduction was observed during 2020 and 2021, followed by an increase in 2022.

This suggests a partial recovery in recorded pedestrian activity relative to sensor-hour observations.

Normalization improves comparability but does not completely account for changes in sensor locations, observation periods, sensor characteristics, or the composition of the sensor network.

The years 2009 and 2022 are partial years in this dataset and should not be compared directly with complete calendar years.

### Retail-planning implication

Yearly analysis provides context for evaluating historical pedestrian movement, disruptions, and recovery. It may help planners avoid using unusually high or low periods as the sole basis for future retail decisions.

---

## 8. Sensor-Level Pedestrian Analysis

Sensor rankings reveal substantial differences in recorded pedestrian movement across individual locations.

### Top locations by cumulative passages

| Rank | Sensor location | Total passages |
|---|---|---:|
| 1 | Town Hall (West) | 145,343,894 |
| 2 | Flinders Street Station Underpass | 125,944,098 |
| 3 | Melbourne Central | 122,043,213 |
| 4 | Princes Bridge | 114,077,134 |
| 5 | Bourke Street Mall (South) | 111,277,028 |
| 6 | Bourke Street Mall (North) | 110,015,010 |

Town Hall (West) recorded the highest cumulative passage volume among the analyzed sensors.

These locations represent areas with substantial recorded pedestrian movement over their available observation periods.

### Total passages versus average passages

Sensor rankings based on cumulative passages may differ from rankings based on average passages per recorded sensor-hour.

For example:

- Town Hall (West) recorded the highest cumulative total.
- Flinders St–Swanston St (West) recorded an unusually high average of approximately 2,448.78 passages per recorded sensor-hour.
- This sensor had only 17,662 sensor-hour records and a recorded status of R.

The difference demonstrates why location comparisons should consider both total passages and average passage rates.

### Retail-planning implication

Sensor rankings can support further investigation of potential high-movement areas for retail location evaluation, site comparison, and mobility analysis.

However, pedestrian movement is only one factor in retail site selection. Rent, accessibility, competition, target customers, purchasing behavior, demographics, store visibility, and commercial performance are not established by this dataset.

---

## 9. Sensor Coverage Investigation

Observation coverage is an important consideration when interpreting sensor-level results.

### Top 10 sensors by recorded sensor-hour observations

| Sensor | Sensor-hour records | Total passages | Avg passages/hour |
|---|---:|---:|---:|
| Bourke Street Mall (South) | 117,379 | 111,277,028 | 948.01 |
| Southern Cross Station | 117,353 | 53,149,677 | 452.90 |
| Flinders Street Station Underpass | 117,185 | 125,944,098 | 1,074.75 |
| Victoria Point | 117,057 | 17,786,144 | 151.94 |
| Waterfront City | 116,100 | 10,853,394 | 93.48 |
| Webb Bridge | 115,681 | 17,141,882 | 148.18 |
| Princes Bridge | 114,260 | 114,077,134 | 998.40 |
| New Quay | 114,109 | 22,405,820 | 196.35 |
| Collins Place (North) | 112,767 | 34,679,974 | 307.54 |
| Melbourne Central | 112,162 | 122,043,213 | 1,088.10 |

The ten sensors with the highest observation counts contain approximately 112,000 to 117,000 sensor-hour records.

Their observation volumes are relatively similar, which allows a more balanced comparison than locations with considerably fewer recorded observations.

Nevertheless, sensor-hour records do not guarantee uninterrupted operation or identical observation periods. Differences in installation dates, missing records, sensor replacement, location changes, and sensor characteristics may affect comparisons.

Recorded status values include A, I, and R. Their meanings have not been independently established within this analysis and should not be interpreted without appropriate metadata documentation.

### Interpretation

Sensor coverage should be considered alongside total passages and average hourly passage counts.

A location with a high average passage rate but relatively few observations may require additional investigation before being treated as a consistently high-activity location.

---

## 10. Consolidated Retail-Planning Implications

The analysis suggests several areas for further investigation.

### 10.1 Staffing and operating schedules

Hourly and weekly pedestrian patterns may help retailers investigate staffing requirements during high-movement periods.

### 10.2 Promotional timing

Midday, afternoon, and Friday activity patterns could be used to formulate hypotheses about when promotions may receive greater pedestrian exposure.

Pedestrian exposure does not guarantee promotion engagement or purchases.

### 10.3 Location evaluation

Sensor rankings may help identify locations with substantial pedestrian movement for further retail-site investigation.

Sensor locations should be evaluated using observation coverage, historical consistency, and location-specific context.

### 10.4 Historical trend monitoring

Monthly and yearly trends can help identify mobility disruptions and recovery periods.

Retail planners should avoid assuming that historical pedestrian patterns are permanently stable.

### 10.5 Further investigation

The findings may support future analyses of sensor clusters, geographic movement, location comparisons, and time-based mobility patterns.

Any retail recommendations should be validated using relevant commercial information before being used in actual business decisions.

---

## 11. Limitations

The findings must be interpreted within the following limitations.

1. **Pedestrian passages are not unique individuals.** A person may be counted multiple times.
2. **Passages do not equal retail customers.** The dataset does not establish that pedestrians entered a store.
3. **Passages do not measure purchases.** Sales, revenue, conversion rates, and purchase value are not available.
4. **Sensor coverage may vary.** Differences in observation periods and missing records may affect comparisons.
5. **Sensor locations and configurations may change.** Historical comparisons may be influenced by changes in the sensor network.
6. **Aggregated results may hide local differences.** Citywide patterns may not reflect an individual street or retail location.
7. **External causes are not directly measured.** The dataset may reveal changes coinciding with major events, but cannot independently establish causation.
8. **Partial calendar years require caution.** The beginning and end of the dataset do not cover complete calendar years.
9. **Sensor status meanings require verification.** Status labels should not be interpreted without reliable documentation.
10. **Normalization is not a complete correction.** Passage counts per sensor-hour improve comparability but do not eliminate sensor-related bias.

---

## 12. Final Conclusion

The GeoPulse analysis identified meaningful patterns in pedestrian movement across Melbourne, including strong hourly variations, differences between weekdays and weekends, historical trends, and considerable variation among sensor locations.

The findings show that pedestrian movement is not evenly distributed across time or location. Recorded activity is concentrated in particular daytime and late-afternoon periods, varies across days of the week, and has experienced substantial historical disruptions.

The analysis also demonstrates the importance of comparing pedestrian passage totals with observation coverage and average passage rates rather than relying on a single metric.

These findings provide an analytical foundation for further hyper-local retail mobility investigation. They may support hypotheses related to staffing, operating schedules, promotional timing, and retail-location evaluation. However, pedestrian passages should not be interpreted as direct measurements of customer demand, purchasing behavior, or sales performance.

The next stage of GeoPulse should focus on presenting these findings through clear visualizations and an interactive analytical dashboard, while maintaining the data quality checks, analytical limitations, and evidence-based interpretation established during this phase.

---

## 13. Project Status

| Phase | Status |
|---|---|
| Project setup and repository initialization | Completed |
| Dataset inventory | Completed |
| Data validation | Completed |
| Exploratory data analysis | Completed |
| Hourly pattern analysis | Completed |
| Weekly pattern analysis | Completed |
| Weekday/weekend comparison | Completed |
| Monthly trend analysis | Completed |
| Yearly trend analysis | Completed |
| Sensor-level ranking | Completed |
| Sensor coverage investigation | Completed |
| Consolidated analytical report | Completed |
| Visualization development | Pending |
| Interactive dashboard | Pending |
