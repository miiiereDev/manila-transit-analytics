# Data Analysis Script - Manila Transit Analytics
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configure directories
INPUT_PATH = os.path.join('data', '2_cleaned', 'manila_transit_cleaned.csv')
FIGURES_DIR = os.path.join('output', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

# Set visual style 
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'figure.dpi': 150
})

# Custom premium palette
PALETTE = {
    'EDSA Carousel': '#E74C3C', # Crimson Red
    'MRT-3': '#3498DB',         # Blue
    'LRT-2': '#9B59B6',         # Purple
    'LRT-1': '#2ECC71'          # Green
}

def load_cleaned_data(path: str) -> pd.DataFrame:
    """Loads the cleaned dataset and checks its size."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cleaned dataset not found at {path}. Please run data_cleaning.py first.")
    df = pd.read_csv(path)
    # Convert station names to uppercase for consistent visual display in charts and tables
    if 'Station_From' in df.columns:
        df['Station_From'] = df['Station_From'].astype(str).str.upper()
    print(f"[LOAD] Loaded {len(df):,} cleaned records.")
    return df

def analyze_overall_performance(df: pd.DataFrame):
    """Answers RQ1: Overall Line Performance."""
    df['Delay'] = df['Actual_Wait_Time'] - df['Scheduled_Interval']
    
    summary = df.groupby('Transit_Line').agg(
        avg_scheduled=('Scheduled_Interval', 'mean'),
        avg_actual=('Actual_Wait_Time', 'mean'),
        avg_delay=('Delay', 'mean')
    ).reset_index()
    
    print("\n=== RQ1: OVERALL LINE PERFORMANCE ===")
    print(summary.to_string(index=False, formatters={
        'avg_scheduled': '{:.2f} mins'.format,
        'avg_actual': '{:.2f} mins'.format,
        'avg_delay': '{:.2f} mins'.format
    }))
    
    # Plot average wait times vs scheduled
    plt.figure(figsize=(8, 5))
    df_melt = df.melt(
        id_vars=['Transit_Line'], 
        value_vars=['Scheduled_Interval', 'Actual_Wait_Time'],
        var_name='Time_Type', value_name='Minutes'
    )
    df_melt['Time_Type'] = df_melt['Time_Type'].map({
        'Scheduled_Interval': 'Scheduled Interval',
        'Actual_Wait_Time': 'Actual Wait Time'
    })
    
    sns.barplot(
        data=df_melt, x='Transit_Line', y='Minutes', hue='Time_Type',
        palette=['#BDC3C7', '#2C3E50'], edgecolor='none', alpha=0.9
    )
    plt.title("Scheduled vs. Actual Wait Time by Transit Line", pad=15)
    plt.xlabel("Transit Line")
    plt.ylabel("Time (minutes)")
    plt.legend(title=None, frameon=True)
    plt.tight_layout()
    
    fig_path = os.path.join(FIGURES_DIR, 'average_wait_time_by_line.png')
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"[PLOT] Saved average wait time by line to '{fig_path}'")

def analyze_peak_impact(df: pd.DataFrame):
    """Answers RQ2: Peak Hour Impact."""
    # Define peak period categorization
    peak_map = {
        'Peak Morning': 'Peak',
        'Peak Evening': 'Peak',
        'Mid-Day': 'Off-Peak',
        'Late Night': 'Off-Peak'
    }
    df['Period_Type'] = df['Time_of_Day'].map(peak_map)
    
    summary = df.groupby(['Transit_Line', 'Period_Type'])['Actual_Wait_Time'].mean().unstack()
    summary['Pct_Increase'] = ((summary['Peak'] - summary['Off-Peak']) / summary['Off-Peak']) * 100
    
    print("\n=== RQ2: PEAK HOUR IMPACT ===")
    print(summary.to_string(formatters={
        'Peak': '{:.2f} mins'.format,
        'Off-Peak': '{:.2f} mins'.format,
        'Pct_Increase': '{:.1f}%'.format
    }))
    
    # Plot Peak vs Off-Peak
    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=df, x='Transit_Line', y='Actual_Wait_Time', hue='Period_Type',
        hue_order=['Off-Peak', 'Peak'], palette=['#7F8C8D', '#D35400'], alpha=0.9
    )
    plt.title("Average Wait Time: Peak vs. Off-Peak Periods", pad=15)
    plt.xlabel("Transit Line")
    plt.ylabel("Actual Wait Time (minutes)")
    plt.legend(title="Period Type", frameon=True)
    plt.tight_layout()
    
    fig_path = os.path.join(FIGURES_DIR, 'peak_vs_offpeak_comparison.png')
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"[PLOT] Saved peak vs off-peak comparison to '{fig_path}'")

def analyze_weather_impact(df: pd.DataFrame):
    """Answers RQ3: Weather Vulnerability."""
    # Group by line and weather condition
    summary = df.groupby(['Transit_Line', 'Weather_Condition'])['Actual_Wait_Time'].mean().unstack()
    
    # Percentage increase during heavy rain compared to dry conditions (Clear & Cloudy average)
    summary['Dry_Avg'] = (summary['Clear'] + summary['Cloudy']) / 2
    summary['Pct_Increase_Rain'] = ((summary['Heavy Rain'] - summary['Dry_Avg']) / summary['Dry_Avg']) * 100
    
    print("\n=== RQ3: WEATHER VULNERABILITY ===")
    print(summary.to_string(formatters={
        'Clear': '{:.2f} mins'.format,
        'Cloudy': '{:.2f} mins'.format,
        'Heavy Rain': '{:.2f} mins'.format,
        'Dry_Avg': '{:.2f} mins'.format,
        'Pct_Increase_Rain': '{:.1f}%'.format
    }))
    
    # Plot Weather Impact
    plt.figure(figsize=(9, 5.5))
    sns.barplot(
        data=df, x='Transit_Line', y='Actual_Wait_Time', hue='Weather_Condition',
        hue_order=['Clear', 'Cloudy', 'Heavy Rain'],
        palette=['#F1C40F', '#95A5A6', '#2980B9'], alpha=0.9
    )
    plt.title("Average Wait Time by Weather Condition", pad=15)
    plt.xlabel("Transit Line")
    plt.ylabel("Actual Wait Time (minutes)")
    plt.legend(title="Weather", frameon=True)
    plt.tight_layout()
    
    fig_path = os.path.join(FIGURES_DIR, 'weather_impact_by_line.png')
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"[PLOT] Saved weather impact by line to '{fig_path}'")

def analyze_worst_stations(df: pd.DataFrame):
    """Answers RQ4: Worst Stations."""
    df['Delay'] = df['Actual_Wait_Time'] - df['Scheduled_Interval']
    
    station_delays = df.groupby(['Transit_Line', 'Station_From'])['Delay'].mean().reset_index()
    top_5_worst = station_delays.sort_values(by='Delay', ascending=False).head(5)
    
    print("\n=== RQ4: TOP 5 WORST PERFORMING STATIONS ===")
    print(top_5_worst.to_string(index=False, formatters={
        'Delay': '{:.2f} mins'.format
    }))
    
    # Plot Top 5 Worst Stations
    plt.figure(figsize=(9, 5))
    top_5_worst['Station_Label'] = top_5_worst['Station_From'] + " (" + top_5_worst['Transit_Line'] + ")"
    
    sns.barplot(
        data=top_5_worst, y='Station_Label', x='Delay', hue='Transit_Line',
        palette=PALETTE, dodge=False, alpha=0.9
    )
    plt.title("Top 5 Stations with Highest Average Delay", pad=15)
    plt.ylabel("Station (Transit Line)")
    plt.xlabel("Average Delay (Actual - Scheduled, minutes)")
    plt.legend(title="Transit Line", frameon=True)
    plt.tight_layout()
    
    fig_path = os.path.join(FIGURES_DIR, 'top_5_worst_stations.png')
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"[PLOT] Saved top 5 worst stations to '{fig_path}'")

if __name__ == "__main__":
    try:
        cleaned_df = load_cleaned_data(INPUT_PATH)
        analyze_overall_performance(cleaned_df)
        analyze_peak_impact(cleaned_df)
        analyze_weather_impact(cleaned_df)
        analyze_worst_stations(cleaned_df)
        print("\n" + "=" * 50)
        print("DATA ANALYSIS COMPLETE — ALL FIGURES GENERATED")
        print("=" * 50)
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
