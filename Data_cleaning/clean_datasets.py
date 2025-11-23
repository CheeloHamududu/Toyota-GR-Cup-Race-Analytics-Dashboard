#!/usr/bin/env python3
import pandas as pd
import os
import numpy as np
from pathlib import Path

def clean_race_results(file_path, output_path):
    """Clean race results CSV files with semicolon delimiters"""
    try:
        df = pd.read_csv(file_path, delimiter=';')
        
        # Remove empty columns
        df = df.dropna(axis=1, how='all')
        
        # Clean numeric columns
        numeric_cols = ['POSITION', 'LAPS', 'FL_LAPNUM', 'FL_KPH']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean time columns
        time_cols = ['TOTAL_TIME', 'GAP_FIRST', 'GAP_PREVIOUS', 'FL_TIME']
        for col in time_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Sort by position
        if 'POSITION' in df.columns:
            df = df.sort_values('POSITION')
        
        df.to_csv(output_path, index=False)
        print(f"Cleaned {file_path} -> {output_path}")
        return len(df)
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
        return 0

def clean_weather_data(file_path, output_path):
    """Clean weather data CSV file"""
    try:
        df = pd.read_csv(file_path, delimiter=';')
        
        # Convert timestamp columns
        if 'TIME_UTC_SECONDS' in df.columns:
            df['TIME_UTC_SECONDS'] = pd.to_numeric(df['TIME_UTC_SECONDS'], errors='coerce')
        
        # Clean numeric weather columns
        numeric_cols = ['AIR_TEMP', 'TRACK_TEMP', 'HUMIDITY', 'PRESSURE', 'WIND_SPEED', 'WIND_DIRECTION', 'RAIN']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove duplicates and sort by time
        df = df.drop_duplicates()
        if 'TIME_UTC_SECONDS' in df.columns:
            df = df.sort_values('TIME_UTC_SECONDS')
        
        df.to_csv(output_path, index=False)
        print(f"Cleaned {file_path} -> {output_path}")
        return len(df)
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
        return 0

def clean_lap_data(file_path, output_path):
    """Clean lap timing data CSV files"""
    try:
        df = pd.read_csv(file_path)
        
        # Clean timestamp columns
        timestamp_cols = ['meta_time', 'timestamp', 'expire_at', 'value']
        for col in timestamp_cols:
            if col in df.columns and col != 'value':
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean numeric columns
        numeric_cols = ['outing', 'lap']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Handle 'value' column based on file type
        if 'value' in df.columns:
            if 'time' in file_path.lower():
                # For time files, convert value to numeric (milliseconds)
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
            else:
                # For start/end time files, keep as timestamp
                df['value'] = pd.to_datetime(df['value'], errors='coerce')
        
        # Remove rows with invalid lap numbers (like 32768)
        if 'lap' in df.columns:
            df = df[df['lap'] < 100]  # Reasonable lap limit
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Sort by vehicle_id, then lap
        if 'vehicle_id' in df.columns and 'lap' in df.columns:
            df = df.sort_values(['vehicle_id', 'lap'])
        
        df.to_csv(output_path, index=False)
        print(f"Cleaned {file_path} -> {output_path}")
        return len(df)
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
        return 0

def clean_telemetry_data(file_path, output_path):
    """Clean large telemetry data file with sampling"""
    try:
        # Read in chunks to handle large file
        chunk_size = 10000
        chunks = []
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            # Basic cleaning for each chunk
            chunk = chunk.dropna(axis=1, how='all')
            chunk = chunk.drop_duplicates()
            
            # Sample every 10th row to reduce size
            chunk = chunk.iloc[::10]
            chunks.append(chunk)
        
        df = pd.concat(chunks, ignore_index=True)
        
        # Final deduplication
        df = df.drop_duplicates()
        
        df.to_csv(output_path, index=False)
        print(f"Cleaned and sampled {file_path} -> {output_path}")
        return len(df)
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
        return 0

def main():
    base_dir = Path("/home/User/Documents/toyota/Race 1")
    output_dir = base_dir / "new data"
    
    # File mapping and cleaning functions
    files_to_clean = [
        ("00_Results GR Cup Race 1 Official_Anonymized.CSV", "race_results_official.csv", clean_race_results),
        ("03_Provisional Results_Race 1_Anonymized.CSV", "race_results_provisional.csv", clean_race_results),
        ("05_Provisional Results by Class_Race 1_Anonymized.CSV", "race_results_by_class.csv", clean_race_results),
        ("23_AnalysisEnduranceWithSections_Race 1_Anonymized.CSV", "endurance_analysis.csv", clean_race_results),
        ("26_Weather_Race 1_Anonymized.CSV", "weather_data.csv", clean_weather_data),
        ("99_Best 10 Laps By Driver_Race 1_Anonymized.CSV", "best_laps_by_driver.csv", clean_race_results),
        ("COTA_lap_end_time_R1.csv", "lap_end_times.csv", clean_lap_data),
        ("COTA_lap_start_time_R1.csv", "lap_start_times.csv", clean_lap_data),
        ("COTA_lap_time_R1.csv", "lap_times.csv", clean_lap_data),
        ("R1_cota_telemetry_data.csv", "telemetry_data_sampled.csv", clean_telemetry_data),
    ]
    
    total_files = 0
    total_rows = 0
    
    print("Starting dataset cleaning process...")
    print("=" * 50)
    
    for input_file, output_file, clean_func in files_to_clean:
        input_path = base_dir / input_file
        output_path = output_dir / output_file
        
        if input_path.exists():
            rows = clean_func(str(input_path), str(output_path))
            total_files += 1
            total_rows += rows
        else:
            print(f"File not found: {input_file}")
    
    print("=" * 50)
    print(f"Cleaning complete!")
    print(f"Total files processed: {total_files}")
    print(f"Total rows in cleaned datasets: {total_rows}")
    print(f"Cleaned files saved to: {output_dir}")

if __name__ == "__main__":
    main()