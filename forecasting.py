"""
NHS GP Appointments Forecasting Analysis
Phase 1, Step 1: Load Full Historical Dataset (Aug 2023 - Jan 2026)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob
from datetime import datetime

# Configuration
data_dir = Path('data/Appointments_GP_Daily_CSV_Jan_26')

def load_all_historical_data():
    """
    Load all 30 CSV files (Aug 2023 - Jan 2026) and concatenate into single DataFrame.
    
    Returns:
        pd.DataFrame: Combined historical appointment data
    """
    print("="*60)
    print("PHASE 1, STEP 1: Loading Full Historical Dataset")
    print("="*60)
    
    # Get all SUB_ICB_LOCATION CSV files (excluding COVERAGE file)
    csv_pattern = str(data_dir / 'SUB_ICB_LOCATION_CSV_*.csv')
    csv_files = sorted(glob.glob(csv_pattern))
    
    print(f"\nFound {len(csv_files)} appointment data files")
    print(f"Expected: 30 files (Aug 2023 - Jan 2026)\n")
    
    if len(csv_files) == 0:
        raise FileNotFoundError(f"No CSV files found matching pattern: {csv_pattern}")
    
    # Load and concatenate all files
    df_list = []
    total_rows = 0
    total_appointments = 0
    
    for i, file_path in enumerate(csv_files, 1):
        file_name = Path(file_path).name
        size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        
        # Load file
        df_temp = pd.read_csv(file_path)
        
        # Parse dates
        df_temp['Appointment_Date'] = pd.to_datetime(
            df_temp['Appointment_Date'], 
            format='%d%b%Y'
        )
        
        rows = len(df_temp)
        appointments = df_temp['COUNT_OF_APPOINTMENTS'].sum()
        
        total_rows += rows
        total_appointments += appointments
        
        df_list.append(df_temp)
        
        print(f"  [{i:2d}/{len(csv_files)}] {file_name:<45} "
              f"({size_mb:5.1f} MB, {rows:,} rows, {appointments:,} appts)")
    
    # Concatenate all dataframes
    print("\n" + "-"*60)
    print("Concatenating all files...")
    df_full = pd.concat(df_list, ignore_index=True)
    
    # Summary statistics
    print("\n" + "="*60)
    print("LOAD COMPLETE - Summary Statistics")
    print("="*60)
    print(f"Total files loaded:        {len(csv_files)}")
    print(f"Total rows:                {len(df_full):,}")
    print(f"Total appointments:        {df_full['COUNT_OF_APPOINTMENTS'].sum():,}")
    print(f"Date range:                {df_full['Appointment_Date'].min().date()} to {df_full['Appointment_Date'].max().date()}")
    print(f"Unique dates:              {df_full['Appointment_Date'].nunique()}")
    print(f"Memory usage:              {df_full.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    print(f"\nUnique Sub-ICB Locations:  {df_full['SUB_ICB_LOCATION_CODE'].nunique()}")
    print(f"Unique ICBs:               {df_full['ICB_ONS_CODE'].nunique()}")
    print(f"Unique Regions:            {df_full['REGION_ONS_CODE'].nunique()}")
    print("="*60 + "\n")
    
    return df_full


if __name__ == "__main__":
    # Execute Step 1: Load full historical dataset
    df_historical = load_all_historical_data()
    
    # Display sample of loaded data
    print("Sample of loaded data (first 10 rows):")
    print(df_historical.head(10))
    
    print("\nColumn names:")
    print(df_historical.columns.tolist())
    
    print("\nData types:")
    print(df_historical.dtypes)
