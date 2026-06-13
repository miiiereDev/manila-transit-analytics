# Data Cleaning Script - Manila Transit Analytics
import pandas as pd
import numpy as np
import os

# =============================================================================
# CONFIGURATION
# Define input and output file paths so they're easy to change in one place.
# =============================================================================
INPUT_PATH  = os.path.join('data', '1_raw', 'manila_transit_raw.csv')
OUTPUT_PATH = os.path.join('data', '2_cleaned', 'manila_transit_cleaned.csv')

# Valid category values — used to detect and fix string inconsistencies
VALID_TRANSIT_LINES = ['EDSA Carousel', 'MRT-3', 'LRT-2', 'LRT-1']
VALID_TIMES_OF_DAY  = ['Peak Morning', 'Mid-Day', 'Peak Evening', 'Late Night']
VALID_WEATHER       = ['Clear', 'Cloudy', 'Heavy Rain']

# Outlier bounds for Actual_Wait_Time (in minutes)
# Values below MIN or above MAX are considered outliers and will be removed
WAIT_TIME_MIN =  0.0
WAIT_TIME_MAX = 120.0


def load_data(path: str) -> pd.DataFrame:
    """
    Loads the raw CSV file into a DataFrame.
    Prints the shape so we know how many rows and columns came in.
    """
    df = pd.read_csv(path)
    print(f"[LOAD]  Loaded {len(df):,} rows × {len(df.columns)} columns from '{path}'")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops exact duplicate rows (all columns match).
    The simulation appended 10 full-row duplicates, so this removes them.
    `keep='first'` keeps the original and drops every copy after it.
    """
    before = len(df)
    df = df.drop_duplicates(keep='first')
    dropped = before - len(df)
    print(f"[DEDUP] Removed {dropped} duplicate row(s). Rows remaining: {len(df):,}")
    return df


def normalize_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fixes string inconsistencies in categorical columns:
      1. Strip leading/trailing whitespace.
      2. Collapse internal multiple spaces into one.
      3. Title-case the value (so 'mrt-3' → 'Mrt-3', handled below).
      4. Re-insert hyphens by fuzzy-matching against the known valid values.

    For each column we compare the cleaned string against the list of valid
    values using a case-insensitive, hyphen/space-insensitive key.  If a
    match is found, we replace the cell with the canonical form; otherwise
    we leave it as-is (it will surface later during validation).
    """

    def make_key(s: str) -> str:
        """Normalisation key: lowercase, no hyphens, no extra spaces."""
        return s.lower().replace('-', '').replace(' ', '')

    def fuzzy_fix(value, valid_list):
        """
        Strips the value down to its normalisation key and looks for a
        match in the valid list.  Returns the canonical string on a hit,
        or the stripped-but-uncorrected value on a miss.
        """
        cleaned = str(value).strip()
        cleaned = ' '.join(cleaned.split())  # collapse internal spaces
        key = make_key(cleaned)
        for valid in valid_list:
            if make_key(valid) == key:
                return valid          # replace with the canonical form
        return cleaned               # no match — return cleaned value

    col_map = {
        'Transit_Line':      VALID_TRANSIT_LINES,
        'Time_of_Day':       VALID_TIMES_OF_DAY,
        'Weather_Condition': VALID_WEATHER,
    }

    # Station_From has too many valid values to enumerate, so we only strip
    # whitespace and normalise internal spaces for that column.
    df['Station_From'] = df['Station_From'].astype(str).str.strip()
    df['Station_From'] = df['Station_From'].str.replace(r'\s+', ' ', regex=True)

    fixed_total = 0
    for col, valid_list in col_map.items():
        original = df[col].copy()
        df[col] = df[col].apply(lambda v: fuzzy_fix(v, valid_list))
        fixed = (original != df[col]).sum()
        fixed_total += fixed
        print(f"[NORM]  '{col}': fixed {fixed} inconsistent value(s).")

    print(f"[NORM]  Total string fixes: {fixed_total}")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fills missing Actual_Wait_Time values using the median wait time
    for the same Transit_Line + Time_of_Day combination.

    Why median instead of mean?
    The dataset still contains outliers at this stage (we remove them next),
    so the median is more robust — it won't be pulled toward extreme values.

    If no matching group exists (edge case), we fall back to the overall median.
    """
    missing_before = df['Actual_Wait_Time'].isna().sum()

    # Compute group-level medians (NaN rows are excluded from the calculation)
    group_median = (
        df.groupby(['Transit_Line', 'Time_of_Day'])['Actual_Wait_Time']
        .transform('median')
    )

    # Fill NaN cells: first try group median, then fall back to global median
    global_median = df['Actual_Wait_Time'].median()
    df['Actual_Wait_Time'] = df['Actual_Wait_Time'].fillna(group_median)
    df['Actual_Wait_Time'] = df['Actual_Wait_Time'].fillna(global_median)

    missing_after = df['Actual_Wait_Time'].isna().sum()
    print(f"[MISS]  Filled {missing_before - missing_after} missing Actual_Wait_Time value(s). "
          f"Remaining NaN: {missing_after}")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes rows where Actual_Wait_Time falls outside the realistic range
    [WAIT_TIME_MIN, WAIT_TIME_MAX].

    The simulation injected two types of Gaussian outliers:
      • Negative outliers  → mean ≈ -15 min  (physically impossible)
      • Extreme outliers   → mean ≈ 500 min  (unrealistically high)

    Both are caught by the simple min/max bounds defined at the top of
    this file, so we don't need IQR or z-score methods here.
    """
    before = len(df)
    mask = df['Actual_Wait_Time'].between(WAIT_TIME_MIN, WAIT_TIME_MAX)
    df = df[mask].copy()
    removed = before - len(df)
    print(f"[OUTL]  Removed {removed} outlier row(s) outside "
          f"[{WAIT_TIME_MIN}, {WAIT_TIME_MAX}] minutes. Rows remaining: {len(df):,}")
    return df


def validate_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops any rows whose categorical columns still hold an unrecognised
    value after normalisation — these are data errors we can't safely fix.

    We print a warning for each bad value so nothing is silently discarded.
    """
    col_map = {
        'Transit_Line':      VALID_TRANSIT_LINES,
        'Time_of_Day':       VALID_TIMES_OF_DAY,
        'Weather_Condition': VALID_WEATHER,
    }

    before = len(df)
    for col, valid_list in col_map.items():
        bad_mask = ~df[col].isin(valid_list)
        if bad_mask.any():
            bad_values = df.loc[bad_mask, col].unique().tolist()
            print(f"[VALID] WARNING — unrecognised values in '{col}': {bad_values}")
            df = df[~bad_mask].copy()

    dropped = before - len(df)
    if dropped:
        print(f"[VALID] Dropped {dropped} row(s) with unrecognised category values.")
    else:
        print(f"[VALID] All categorical values are valid.")
    return df


def round_numerics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rounds all numeric columns to 2 decimal places for a clean, consistent output.
    Uses pandas built-in round() which applies to every float column automatically.
    """
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    df[numeric_cols] = df[numeric_cols].round(2)
    print(f"[ROUND] Rounded {len(numeric_cols)} numeric column(s) to 2 decimal places: {numeric_cols}")
    return df


def reset_and_sort(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts the cleaned DataFrame by Transit_Line then Trip_ID for readability,
    and resets the integer index so it runs from 0 without gaps.
    """
    df = df.sort_values(['Transit_Line', 'Trip_ID']).reset_index(drop=True)
    print(f"[SORT]  Sorted by Transit_Line → Trip_ID. Index reset.")
    return df


def save_data(df: pd.DataFrame, path: str) -> None:
    """
    Saves the cleaned DataFrame to a CSV file.
    Creates parent directories if they don't exist yet.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[SAVE]  Cleaned data saved to '{path}'")


def print_summary(df: pd.DataFrame) -> None:
    """
    Prints a quick summary of the cleaned dataset so you can verify
    the output at a glance without opening the CSV.
    """
    print("\n" + "=" * 50)
    print("CLEANING COMPLETE — FINAL SUMMARY")
    print("=" * 50)
    print(f"Total rows  : {len(df):,}")
    print(f"Total columns: {len(df.columns)}")
    print(f"\nColumn dtypes:\n{df.dtypes}")
    print(f"\nMissing values per column:\n{df.isna().sum()}")
    print(f"\nActual_Wait_Time stats:\n{df['Actual_Wait_Time'].describe().round(2)}")
    print("=" * 50)


# =============================================================================
# MAIN PIPELINE
# Each step calls one focused function.  The order matters:
#   1. Deduplicate first   — avoids skewing medians used in imputation
#   2. Normalise strings   — must happen before category validation
#   3. Fill missing values — after dedup so medians are accurate
#   4. Remove outliers     — after imputation so filled values aren't lost
#   5. Validate categories — final safety net
#   6. Sort & reset index  — cosmetic, done last
# =============================================================================
if __name__ == "__main__":
    df = load_data(INPUT_PATH)
    df = remove_duplicates(df)
    df = normalize_categorical(df)
    df = handle_missing_values(df)
    df = remove_outliers(df)
    df = validate_categories(df)
    df = round_numerics(df)
    df = reset_and_sort(df)
    save_data(df, OUTPUT_PATH)
    print_summary(df)