import pandas as pd
import numpy as np
import random
import os

# --- DIRTY DATA CONFIGURATION ---
# Adjust these constants to easily control how much "bad data" is injected into the dataset
CONFIG = {
    'target_rows': 1000,              # Base number of rows before duplicates
    'missing_ratio': 0.05,           # 5% of rows will have missing (NaN) Actual_Wait_Time
    'inconsistent_ratio': 0.08,      # 8% of rows will have string formatting inconsistencies
    'outlier_count': 20,             # Total Gaussian outliers (split 50/50 neg/extreme)
    'duplicate_count': 10            # Number of duplicated rows appended at the end
}

def introduce_string_inconsistency(val):
    """
    Randomly mutates a string to simulate human data entry errors.
    Applies variations like casing changes, extra whitespace, or missing hyphens.
    """
    val = str(val)
    mutations = [
        lambda x: x.lower(),                  # 'MRT-3' -> 'mrt-3'
        lambda x: x.upper(),                  # 'Peak Morning' -> 'PEAK MORNING'
        lambda x: f"  {x} ",                  # Extra whitespace: 'Clear' -> '  Clear '
        lambda x: x.replace('-', ' '),        # 'MRT-3' -> 'MRT 3'
        lambda x: x.replace(' ', ''),         # 'North Ave' -> 'NorthAve'
        lambda x: x.swapcase()                # 'Cubao' -> 'cUBAO'
    ]
    mutation = random.choice(mutations)
    return mutation(val)

def generate_manila_transit_data():
    """
    Generates a geographically accurate 'dirty' dataset for Metro Manila transit wait times.
    Utilizes configurable logic and Gaussian distributions for realistic data injection.
    """
    output_path = os.path.join('data', '1_raw', 'manila_transit_raw.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Geographic mappings
    transit_system = {
        'EDSA Carousel': [
            'Monumento Terminal', 'Bagong Barrio', 'Balintawak', 'Kaingin',
            'Roosevelt', 'SM North EDSA', 'North Avenue', 'Philam Q.C.',
            'Quezon Avenue', 'Kamuning', 'Nepa Q. Mart', 'Main Avenue',
            'Santolan', 'Ortigas', 'Guadalupe', 'Buendia', 'Ayala',
            'Tramo', 'Taft Avenue', 'Roxas Boulevard', 'SM Mall of Asia',
            'BVA', 'Macapagal/Aseana', 'PITX Terminal'
        ],
        'MRT-3': [
            'North Avenue', 'Quezon Avenue', 'Kamuning', 'Cubao', 'Santolan-Annapolis',
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
    for i in range(1, CONFIG['target_rows'] + 1):
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

    # 2. CONFIGURABLE DIRTY DATA INJECTION
    
    # A. Missing Values
    missing_count = int(len(df) * CONFIG['missing_ratio'])
    missing_indices = df.sample(n=missing_count).index
    df.loc[missing_indices, 'Actual_Wait_Time'] = np.nan

    # B. Inconsistent Strings (Applied to ALL categorical columns)
    string_cols = ['Transit_Line', 'Station_From', 'Time_of_Day', 'Weather_Condition']
    inconsistent_count = int(len(df) * CONFIG['inconsistent_ratio'])
    inconsistent_indices = df.sample(n=inconsistent_count).index
    
    for idx in inconsistent_indices:
        # Pick a random string column to mangle for this row
        col_to_mangle = random.choice(string_cols)
        original_val = df.loc[idx, col_to_mangle]
        df.loc[idx, col_to_mangle] = introduce_string_inconsistency(original_val)

    # C. GAUSSIAN OUTLIERS
    outlier_indices = df.sample(n=CONFIG['outlier_count']).index
    half_outliers = len(outlier_indices) // 2
    neg_indices = outlier_indices[:half_outliers]
    extreme_indices = outlier_indices[half_outliers:]
    
    df.loc[neg_indices, 'Actual_Wait_Time'] = np.random.normal(loc=-15.0, scale=3.0, size=len(neg_indices))
    df.loc[extreme_indices, 'Actual_Wait_Time'] = np.random.normal(loc=500.0, scale=75.0, size=len(extreme_indices))

    # D. Duplicates
    duplicates = df.sample(n=CONFIG['duplicate_count'])
    df = pd.concat([df, duplicates], ignore_index=True)

    # Final Rounding to keep the numerical data visually clean
    df['Actual_Wait_Time'] = df['Actual_Wait_Time'].round(2)

    # 3. Save and Report
    df.to_csv(output_path, index=False)
    
    print("-" * 50)
    print("CONFIGURABLE DATA SIMULATION COMPLETE")
    print("-" * 50)
    print(f"Total Rows Generated: {len(df)}")
    print(f"Missing Values Injected: {missing_count}")
    print(f"String Inconsistencies Injected: {inconsistent_count} (Spread across {', '.join(string_cols)})")
    print(f"Negative Gaussian Outliers: {len(neg_indices)}")
    print(f"Extreme Gaussian Outliers: {len(extreme_indices)}")
    print(f"Duplicate Rows Added: {CONFIG['duplicate_count']}")
    print("-" * 50)

if __name__ == "__main__":
    generate_manila_transit_data()
