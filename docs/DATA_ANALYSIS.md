# Data Analysis Plan: Manila Transit Analytics (Simplified)

This document details the simplified analytical framework, key metrics, and planned computations for the research titled **"Manila Transit Analytics: Understanding the Intersection of Time, Weather, and Public Transport Reliability."**

---

## 1. Simplified Research Questions (RQs)

We focus on four straightforward, commuter-centric questions to assess the reliability of Metro Manila's transit systems:

1. **RQ1 (Line Performance)**: Which transit line experiences the longest average actual wait times and delays?
2. **RQ2 (Peak Hour Impact)**: How much longer do commuters wait during peak hours (morning/evening) compared to off-peak periods?
3. **RQ3 (Weather Vulnerability)**: How does heavy rain affect wait times across the different transit lines? Is the road-based transit system (EDSA Carousel) affected more than the train systems (MRT-3, LRT-1, LRT-2)?
4. **RQ4 (Worst Stations)**: Which individual stations have the longest average wait times across the entire network?

---

## 2. Key Metrics

To answer these questions, we will compute the following basic metrics from the cleaned dataset:

### A. Absolute Delay (minutes)
The direct difference between actual wait time and the scheduled interval:
$$\text{Delay} = \text{Actual\_Wait\_Time} - \text{Scheduled\_Interval}$$

### B. Average (Mean) Wait Time and Delay
Computed by grouping the data by different categories (Line, Time of Day, Weather) and calculating the mean.

### C. Percentage Increase in Wait Time
To measure the impact of peak hours and rain:
$$\text{Percentage Increase} = \left( \frac{\text{Mean Wait Time (Disrupted)} - \text{Mean Wait Time (Baseline)}}{\text{Mean Wait Time (Baseline)}} \right) \times 100\%$$
* For peak hours, the baseline is off-peak periods (`Mid-Day` and `Late Night`).
* For rain, the baseline is clear/cloudy weather.

---

## 3. Planned Computations (using pandas)

The analysis script will perform the following grouping and aggregation operations:

### Step 1: Overall Line Performance
* Group by `Transit_Line` to calculate the mean `Actual_Wait_Time`, mean `Scheduled_Interval`, and mean `Delay`.

### Step 2: Temporal Analysis (Peak vs. Off-Peak)
* Create a column categorizing `Time_of_Day` into:
  * **Peak**: `Peak Morning`, `Peak Evening`
  * **Off-Peak**: `Mid-Day`, `Late Night`
* Group by `Transit_Line` and `Peak_Period` to compare average wait times and compute the percentage increase.

### Step 3: Weather Analysis (Rain Impact)
* Group by `Transit_Line` and `Weather_Condition` to compare average wait times.
* Calculate the percentage increase in wait time during `Heavy Rain` for each line.

### Step 4: Station Ranking
* Group by `Transit_Line` and `Station_From` to compute the average `Delay`.
* Sort the results to identify the top 5 worst stations.

---

## 4. Planned Visualizations (to save in `output/figures/`)

We will generate four clean, easy-to-read charts:
1. **`average_wait_time_by_line.png`**: A bar chart comparing the scheduled interval against the actual wait time for each transit line.
2. **`peak_vs_offpeak_comparison.png`**: A grouped bar chart showing the average wait time during peak vs. off-peak hours for each line.
3. **`weather_impact_by_line.png`**: A grouped bar chart showing the average wait time under clear, cloudy, and rainy weather for each line.
4. **`top_5_worst_stations.png`**: A horizontal bar chart showing the top 5 stations with the highest average delay.
