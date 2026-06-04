import pandas as pd
import numpy as np
import random
import os

def generate_manila_transit_data():
    """
    Generates a geographically accurate 'dirty' dataset for Metro Manila transit wait times.
    Tracks EDSA Carousel, MRT-3, and LRT-2 with realistic line-specific stations.
    """
    
    # Configuration
    target_rows = 720  # 700 rows at least 
    output_path = os.path.join('data', '1_raw', 'manila_transit_raw.csv')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Geographic mapping
    transit_system = {
        'EDSA Carousel': [
            'Monumento Terminal', 'Bagong Barrio', 'Balintawak', 'Kaingin Road', 
            'Roosevelt', 'SM North EDSA', 'North Ave', 'Philam', 'Quezon Ave', 
            'Kamuning', 'Nepa Q. Mart', 'Main Avenue', 'Cubao-Magallanes', 
            'Santolan-Annapolis', 'Ortigas', 'Guadalupe', 'Buendia', 'Ayala', 
            'Tramo', 'Taft Ave', 'Roxas Blvd', 'SM Mall of Asia', 'BVA / City of Dreams', 
            'Macapagal/Aseana', 'Kennedy Road', 'PITX Terminal'
        ],
        'MRT-3': [
            'North Ave', 'Quezon Ave', 'Kamuning', 'Cubao', 'Santolan-Annapolis', 
            'Ortigas', 'Shaw Blvd', 'Boni', 'Guadalupe', 'Buendia', 'Ayala', 
            'Magallanes', 'Taft Ave'
        ],
        'LRT-2': [
            'Recto', 'Legarda', 'Pureza', 'V. Mapa', 'J. Ruiz', 'Gilmore', 
            'Betty Go-Belmonte', 'Cubao', 'Anonas', 'Katipunan', 'Santolan', 
            'Marikina-Pasay', 'Antipolo'
        ]
    }
    
    times = ['Peak Morning', 'Mid-Day', 'Peak Evening', 'Late Night']
    weather = ['Clear', 'Cloudy', 'Heavy Rain']

    data = []
    for i in range(1, target_rows + 1):
        trip_id = f'TRIP_{i:03d}'
        
        # Geographically accurate pick: pick line first, then pick an actual station on that line
        line = random.choice(list(transit_system.keys()))
        station = random.choice(transit_system[line])
        
        time_of_day = random.choice(times)
        cond = random.choice(weather)
        
        # Base scheduled interval (5 to 10 mins)
        scheduled = random.randint(5, 10)
        
        # --- REALISTIC DELAY LOGIC ---
        # Base multiplier for rush hour
        time_multiplier = 1.0
        if time_of_day in ['Peak Morning', 'Peak Evening']:
            time_multiplier = 2.5  # Heavy rush hour multiplier
        elif time_of_day == 'Late Night':
            time_multiplier = 0.8  # Shorter intervals/less congestion
            
        # Weather impact (EDSA Carousel suffers worst in Heavy Rain compared to trains)
        weather_delay = 0
        if cond == 'Heavy Rain':
            if line == 'EDSA Carousel':
                weather_delay = np.random.gamma(5, 3)
            else:
                weather_delay = np.random.gamma(3, 1.5) # Train technical/slip delays
        else:
            weather_delay = np.random.gamma(1.5, 1.5)

        # Calculate actual wait time based on factors
        actual = (scheduled * time_multiplier) + weather_delay
        
        data.append([trip_id, line, station, time_of_day, scheduled, round(actual, 2), cond])

    # Create DataFrame
    columns = [
        'Trip_ID', 'Transit_Line', 'Station_From', 'Time_of_Day', 
        'Scheduled_Interval', 'Actual_Wait_Time', 'Weather_Condition'
    ]
    df = pd.DataFrame(data, columns=columns)

    # 2. Injecting "Dirty Data" (10-15% of rows for cleaning rubric)
    
    # A. Missing Values (NaN) in Actual_Wait_Time (~5%)
    missing_indices = df.sample(frac=0.05).index
    df.loc[missing_indices, 'Actual_Wait_Time'] = np.nan

    # B. Inconsistent Entries in Transit_Line
    for idx in df.sample(frac=0.04).index:
        current_line = df.loc[idx, 'Transit_Line']
        if current_line == 'MRT-3':
            inconsistency = random.choice(['mrt-3', 'MRT 3', 'MRT-3  ', ' MRT-3'])
            df.loc[idx, 'Transit_Line'] = inconsistency
        elif current_line == 'EDSA Carousel':
            inconsistency = random.choice(['edsa carousel', 'EDSA Carousel  ', 'Edsa Carousel'])
            df.loc[idx, 'Transit_Line'] = inconsistency

    # C. Outliers/Noise in Actual_Wait_Time (Negative or Extreme values)
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
    print("MANILA TRANSIT GEOGRAPHICALLY CORRECT DATA SIMULATION COMPLETE")
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