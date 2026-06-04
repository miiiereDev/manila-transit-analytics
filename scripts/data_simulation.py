import pandas as pd
import numpy as np
import random
import os

def generate_manila_transit_data():
    """
    Generates a geographically accurate 'dirty' dataset for Metro Manila transit wait times.
    Utilizes Gaussian distributions for realistic 'dirty data' injection.
    """
    
    # Configuration
    target_rows = 720 
    output_path = os.path.join('data', '1_raw', 'manila_transit_raw.csv')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Geographic mappings
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
        ],
        'LRT-1': [
            'Fernando Poe Jr. (Roosevelt)', 'Balintawak', 'Monumento', '5th Avenue', 
            'R. Papa', 'Abad Santos', 'Blumentritt', 'Tayuman', 'Bambang', 
            'Doroteo Jose', 'Carriedo', 'Central Terminal', 'UN Avenue', 'Pedro Gil', 
            'Quirino', 'Vito Cruz', 'Gil Puyat', 'Libertad', 'EDSA', 'Baclaran',
            'Redemptorist', 'MIA', 'Asia World', 'Ninoy Aquino', 'Dr. Santos'
        ]
    }
    
    times = ['Peak Morning', 'Mid-Day', 'Peak Evening', 'Late Night']
    weather = ['Clear', 'Cloudy', 'Heavy Rain']

    data = []
    for i in range(1, target_rows + 1):
        trip_id = f'TRIP_{i:03d}'
        line = random.choice(list(transit_system.keys()))
        station = random.choice(transit_system[line])
        time_of_day = random.choice(times)
        cond = random.choice(weather)
        
        # Base scheduled interval
        scheduled = random.randint(5, 10)
        
        # Realistic Delay Logic
        time_multiplier = 1.0
        if time_of_day in ['Peak Morning', 'Peak Evening']:
            time_multiplier = 2.5 
        elif time_of_day == 'Late Night':
            time_multiplier = 0.8 
            
        weather_delay = 0
        if cond == 'Heavy Rain':
            weather_delay = np.random.gamma(5, 3) if line == 'EDSA Carousel' else np.random.gamma(3, 1.5)
        else:
            weather_delay = np.random.gamma(1.5, 1.5)

        actual = (scheduled * time_multiplier) + weather_delay
        data.append([trip_id, line, station, time_of_day, scheduled, round(actual, 2), cond])

    columns = ['Trip_ID', 'Transit_Line', 'Station_From', 'Time_of_Day', 'Scheduled_Interval', 'Actual_Wait_Time', 'Weather_Condition']
    df = pd.DataFrame(data, columns=columns)

    # 2. ENHANCED GAUSSIAN DIRTY DATA INJECTION
    
    # A. Missing Values (Standard)
    missing_indices = df.sample(frac=0.05).index
    df.loc[missing_indices, 'Actual_Wait_Time'] = np.nan

    # B. Inconsistent Strings
    for idx in df.sample(frac=0.04).index:
        current_line = df.loc[idx, 'Transit_Line']
        if current_line == 'MRT-3':
            df.loc[idx, 'Transit_Line'] = random.choice(['mrt-3', 'MRT 3', 'MRT-3  '])
        elif current_line == 'EDSA Carousel':
            df.loc[idx, 'Transit_Line'] = random.choice(['edsa carousel', 'EDSA Carousel  ', 'Edsa Carousel'])

    # C. GAUSSIAN OUTLIERS (Statistical Noise)
    # We'll use 20 rows for these sophisticated outliers
    outlier_indices = df.sample(n=20).index
    
    # Split the outliers: 10 Negative (Impossible), 10 Extreme (Unrealistic)
    neg_indices = outlier_indices[:10]
    extreme_indices = outlier_indices[10:]

    # Generate values using Gaussian Distribution
    # loc=Mean, scale=Standard Deviation
    df.loc[neg_indices, 'Actual_Wait_Time'] = np.random.normal(loc=-15.0, scale=3.0, size=len(neg_indices))
    df.loc[extreme_indices, 'Actual_Wait_Time'] = np.random.normal(loc=500.0, scale=75.0, size=len(extreme_indices))

    # D. Duplicates
    duplicates = df.sample(n=10)
    df = pd.concat([df, duplicates], ignore_index=True)

    # Final Rounding to keep it clean looking
    df['Actual_Wait_Time'] = df['Actual_Wait_Time'].round(2)

    # 3. Save and Report
    df.to_csv(output_path, index=False)
    
    print("-" * 50)
    print("ENHANCED GAUSSIAN DATA SIMULATION COMPLETE")
    print("-" * 50)
    print(f"Total Rows: {len(df)}")
    print(f"Negative Gaussian Outliers (Mean ~ -15): 10")
    print(f"Extreme Gaussian Outliers (Mean ~ 500): 10")
    print("-" * 50)

if __name__ == "__main__":
    generate_manila_transit_data()
