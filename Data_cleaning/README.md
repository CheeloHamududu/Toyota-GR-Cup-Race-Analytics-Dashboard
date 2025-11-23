# Toyota Racing Data Cleaning Project

This project processes and cleans racing data from Toyota GR Cup Race 1 at Circuit of the Americas (COTA). The cleaning pipeline standardizes various data formats and prepares them for analysis.

## Data Cleaning Process

### Overview
The `clean_datasets.py` script processes 10 different racing datasets, applying specific cleaning functions based on data type:

1. **Race Results Data** - Official and provisional race results
2. **Weather Data** - Environmental conditions during the race
3. **Lap Timing Data** - Individual lap times and timestamps
4. **Telemetry Data** - High-frequency vehicle sensor data

### Cleaning Steps

#### Race Results Cleaning
- Removes empty columns and duplicate rows
- Converts numeric columns (POSITION, LAPS, FL_LAPNUM, FL_KPH) to proper data types
- Standardizes time format columns (TOTAL_TIME, GAP_FIRST, GAP_PREVIOUS, FL_TIME)
- Sorts results by position

#### Weather Data Cleaning
- Converts timestamps to numeric format
- Standardizes weather measurements (temperature, humidity, pressure, wind, rain)
- Removes duplicates and sorts by time

#### Lap Data Cleaning
- Converts timestamps to datetime format
- Handles lap timing values (milliseconds for lap times, timestamps for start/end times)
- Filters out invalid lap numbers (>100)
- Sorts by vehicle and lap number

#### Telemetry Data Cleaning
- Processes large files in chunks (10,000 rows at a time)
- Samples every 10th row to reduce file size
- Removes duplicates and empty columns

## Datasets Used

### Input Files (Raw Data)
| File | Description | Cleaning Function |
|------|-------------|-------------------|
| `00_Results GR Cup Race 1 Official_Anonymized.CSV` | Official race results | `clean_race_results` |
| `03_Provisional Results_Race 1_Anonymized.CSV` | Provisional race results | `clean_race_results` |
| `05_Provisional Results by Class_Race 1_Anonymized.CSV` | Results grouped by racing class | `clean_race_results` |
| `23_AnalysisEnduranceWithSections_Race 1_Anonymized.CSV` | Endurance race analysis with track sections | `clean_race_results` |
| `26_Weather_Race 1_Anonymized.CSV` | Weather conditions throughout the race | `clean_weather_data` |
| `99_Best 10 Laps By Driver_Race 1_Anonymized.CSV` | Top 10 fastest laps per driver | `clean_race_results` |
| `COTA_lap_end_time_R1.csv` | Lap completion timestamps | `clean_lap_data` |
| `COTA_lap_start_time_R1.csv` | Lap start timestamps | `clean_lap_data` |
| `COTA_lap_time_R1.csv` | Individual lap times | `clean_lap_data` |
| `R1_cota_telemetry_data.csv` | Vehicle telemetry data (large file) | `clean_telemetry_data` |

### Output Files (Cleaned Data)
All cleaned files are saved to the `new data/` directory:

| Output File | Source | Purpose |
|-------------|--------|---------|
| `race_results_official.csv` | Official results | Final race standings |
| `race_results_provisional.csv` | Provisional results | Preliminary race standings |
| `race_results_by_class.csv` | Class results | Results segmented by racing class |
| `endurance_analysis.csv` | Endurance analysis | Performance analysis with track sections |
| `weather_data.csv` | Weather data | Environmental conditions |
| `best_laps_by_driver.csv` | Best laps | Top performance metrics per driver |
| `lap_end_times.csv` | Lap end times | Lap completion timestamps |
| `lap_start_times.csv` | Lap start times | Lap initiation timestamps |
| `lap_times.csv` | Lap times | Individual lap performance |
| `telemetry_data_sampled.csv` | Telemetry (sampled) | Vehicle sensor data (reduced size) |

## Usage

### Prerequisites
```bash
pip install pandas numpy pathlib
```

### Running the Cleaning Process
```bash
python clean_datasets.py
```

### Expected Output
- Processes all available input files
- Creates cleaned versions in `new data/` directory
- Displays progress and summary statistics
- Reports total files processed and row counts

## Data Quality Notes

- **Missing Files**: Script continues if input files are missing
- **Data Validation**: Numeric columns are validated with error handling
- **Size Optimization**: Telemetry data is sampled to reduce file size
- **Duplicate Removal**: All datasets are deduplicated
- **Sorting**: Data is logically sorted (by position, time, or lap number)

## Next Steps

After cleaning, the standardized datasets can be used for:
- Race performance analysis
- Weather impact studies
- Lap time optimization
- Telemetry-based insights
- Driver comparison studies