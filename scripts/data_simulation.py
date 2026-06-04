import pandas as pd
import numpy as np
import random
import os

def generate_manila_transit_data():
    """
    Generates a simulated 'dirty' dataset for Metro Manila transit wait times.
    Targets: EDSA Carousel, MRT-3, and LRT-2.
    """
    
    # Configuration
    target_rows = 720  # Exceed the 700 row requirement
    output_path = os.path.join('data', '1_raw', 'manila_transit_raw.csv')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Base Data Generation
    lines = ['EDSA Carousel', 'MRT-3', 'LRT-2']
    stations = ['North Ave', 'Cubao', 'Taft Ave', 'Santolan', 'Ayala', 'Boni', 'Recto', 'Shaw Blvd']
    times = ['Peak Morning', 'Mid-Day', 'Peak Evening', 'Late Night']
    weather = ['Clear', 'Cloudy', 'Heavy Rain']

    data = []
    for i in range(1, target_rows + 1):
        trip_id = f'TRIP_{i:03d}'
        line = random.choice(lines)
        station = random.choice(stations)
        time_of_day = random.choice(times)
        
        # Base scheduled interval (5 to 10 mins)
        scheduled = random.randint(5, 10)
        
        # Base actual wait time (scheduled + some random delay)
        # We use a gamma distribution to simulate realistic wait time variance
        actual = scheduled + np.random.gamma(2, 2) 
        
        cond = random.choice(weather)
        
        data.append([trip_id, line, station, time_of_day, scheduled, round(actual, 2), cond])

    # Create DataFrame
    columns = [
        'Trip_ID', 'Transit_Line', 'Station_From', 'Time_of_Day', 
        'Scheduled_Interval', 'Actual_Wait_Time', 'Weather_Condition'
    ]
    df = pd.DataFrame(data, columns=columns)

    # 2. Injecting "Dirty Data" (10-15% of rows)
    
    # A. Missing Values (NaN) in Actual_Wait_Time (~5%)
    missing_indices = df.sample(frac=0.05).index
    df.loc[missing_indices, 'Actual_Wait_Time'] = np.nan

    # B. Inconsistent Entries in Transit_Line
    # We'll target MRT-3 and EDSA Carousel for string inconsistencies
    for idx in df.sample(frac=0.04).index:
        current_line = df.loc[idx, 'Transit_Line']
        if current_line == 'MRT-3':
            inconsistency = random.choice(['mrt-3', 'MRT 3', 'MRT-3  ', ' MRT-3'])
            df.loc[idx, 'Transit_Line'] = inconsistency
        elif current_line == 'EDSA Carousel':
            inconsistency = random.choice(['edsa carousel', 'EDSA Carousel  ', 'Edsa Carousel'])
            df.loc[idx, 'Transit_Line'] = inconsistency

    # C. Outliers/Noise in Actual_Wait_Time
    # Injecting impossible values (-5) or extreme values (999)
    outlier_indices = df.sample(n=10).index
    for i, idx in enumerate(outlier_indices):
        if i % 2 == 0:
            df.loc[idx, 'Actual_Wait_Time'] = -5.0
        else:
            df.loc[idx, 'Actual_Wait_Time'] = 999.0

    # D. Duplicates (5-10 completely identical rows)
    duplicates = df.sample(n=8)
    df = pd.concat([df, duplicates], ignore_index=True)

    # 3. Save and Report
    df.to_csv(output_path, index=False)
    
    print("-" * 50)
    print("MANILA TRANSIT DATA SIMULATION COMPLETE")
    print("-" * 50)
    print(f"File Saved: {output_path}")
    print(f"Total Rows Generated: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print("\nInjected Error Summary:")
    print(f"- Missing 'Actual_Wait_Time' values: {len(missing_indices)}")
    print(f"- Outliers (Negative/Extreme): 10")
    print(f"- Duplicate Rows added: 8")
    print("- Inconsistent 'Transit_Line' strings injected randomly.")
    print("-" * 50)

if __name__ == "__main__":
    generate_manila_transit_data()
