# Data Cleaning Documentation

This document provides a technical overview of how the `scripts/data_cleaning.py` module processes, cleans, and normalizes the raw transit dataset for the Manila Transit Analytics project.

## 1. Overview
The data cleaning pipeline takes the raw, simulated Metro Manila transit dataset containing statistical noise, missing values, duplicates, and string inconsistencies, and transforms it into a clean, structured, and validated dataset ready for analysis.

## 2. Configuration & Bounds
The script is configured using global constants defined at the top of the file:
- **Input Path**: `data/1_raw/manila_transit_raw.csv`
- **Output Path**: `data/2_cleaned/manila_transit_cleaned.csv`
- **Valid Categorical Values**:
  - `Transit_Line`: `'EDSA Carousel'`, `'MRT-3'`, `'LRT-2'`, `'LRT-1'`
  - `Time_of_Day`: `'Peak Morning'`, `'Mid-Day'`, `'Peak Evening'`, `'Late Night'`
  - `Weather_Condition`: `'Clear'`, `'Cloudy'`, `'Heavy Rain'`
- **Wait Time Bounds**:
  - `WAIT_TIME_MIN`: `0.0` minutes
  - `WAIT_TIME_MAX`: `120.0` minutes

## 3. Pipeline Steps & Core Logic
The pipeline executes a series of sequential operations where the order is critical to avoid bias and data loss:

### A. Load Data (`load_data`)
Loads the raw CSV dataset from `INPUT_PATH` using `pandas.read_csv` and outputs its shape.

### B. Deduplication (`remove_duplicates`)
Exact duplicates (where all columns match) are removed keeping only the first occurrence (`keep='first'`).
> [!IMPORTANT]
> Deduplication must happen **before** handling missing values or calculating statistical metrics, ensuring that duplicate records do not skew the median wait times used in imputation.

### C. Categorical Normalization (`normalize_categorical`)
Corrects string inconsistencies injected during simulation:
1. Strips leading and trailing whitespaces.
2. Collapses multiple internal spaces into a single space.
3. Applies a fuzzy matching normalization key (lowercase, no hyphens, no spaces) to verify and map inputs to their canonical forms (e.g., `'mrt-3'` or `'MRT 3'` $\rightarrow$ `'MRT-3'`).
4. Strips and normalizes whitespaces in the `Station_From` column.

### D. Imputing Missing Values (`handle_missing_values`)
Populates missing `Actual_Wait_Time` values (sensor failure / logging errors) using:
1. The **median** wait time grouped by the combination of `Transit_Line` and `Time_of_Day`.
2. A fallback to the global **median** if no matching group exists.
> [!TIP]
> The **median** is preferred over the mean as it is more robust to extreme values/outliers which have not yet been removed from the dataset.

### E. Outlier Removal (`remove_outliers`)
Removes entries where `Actual_Wait_Time` is outside the realistic window $[0, 120]$ minutes. This filters out the simulated:
- **Impossible Negatives** ($\approx -15$ mins) representing underflow errors.
- **Extreme Delays** ($\approx 500$ mins) representing system glitches or "ghost" data.

### F. Categorical Validation (`validate_categories`)
Validates that values in `Transit_Line`, `Time_of_Day`, and `Weather_Condition` belong to the known canonical lists. Rows with unrecognized values (that could not be corrected during normalization) are safely discarded, and warnings are printed.

### G. Numeric Rounding (`round_numerics`)
Rounds all numeric columns (like `Actual_Wait_Time`) to 2 decimal places to ensure neat, uniform output formats.

### H. Sorting and Indexing (`reset_and_sort`)
Sorts the dataset chronologically/structurally by `Transit_Line` and `Trip_ID`, then resets the DataFrame index to be contiguous from 0 without gaps.

### I. Save and Summary (`save_data`, `print_summary`)
Saves the finalized DataFrame to the `OUTPUT_PATH` (automatically creating parent directories if missing) and outputs a detailed final summary showing:
- Total rows and columns.
- Data types of columns.
- Missing value counts.
- Summary statistics for `Actual_Wait_Time`.

## 4. Usage
To clean the raw dataset, run the cleaning pipeline from the project root directory:
```powershell
python scripts/data_cleaning.py
```
Upon successful execution, the cleaned file is saved to `data/2_cleaned/manila_transit_cleaned.csv`.
