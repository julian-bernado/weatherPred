# import libraries
import os
import numpy as np
import pandas as pd

# relative file path to the processed data
noaa_data_path = os.path.join(os.path.dirname(__file__), 'raw_data/noaa/to_csv')
out_path = os.path.join(os.path.dirname(__file__), 'processed_data')
noaa_files = os.listdir(noaa_data_path)

# function to perform feature engineering on each city's climate dataset that was converted to .csv.
def feature_engineering_noaa_climate_data(file_path: str) -> pd.DataFrame:
    """
    :param file_path: Path to the CSV file containing the climate data for a specific city.
    :returns: A pandas DataFrame with the feature-engineered climate data.
    """
    # Load the dataset
    df = pd.read_csv(file_path, parse_dates=['DATE'])

    # Climate variables of interest
    climate_vars = ['PRCP', 'TMIN', 'TAVG', 'TMAX']
    df = df[['DATE'] + climate_vars]

    # Convert temperature variables from tenths of a degree Celsius to Farenheit
    # (see NOAA docs: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt)
    df['TMIN'] = df['TMIN'] / 10 * (9 / 5) + 32
    df['TAVG'] = df['TAVG'] / 10 * (9 / 5) + 32
    df['TMAX'] = df['TMAX'] / 10 * (9 / 5) + 32

    # Add year, month columns for plotting
    df['YEAR'] = df['DATE'].dt.year
    df['MONTH'] = df['DATE'].dt.month

    # Add a column for the day of the year
    df['DAY_OF_YEAR'] = df['DATE'].dt.dayofyear

    # Add a column for the week of the year
    df['WEEK_OF_YEAR'] = df['DATE'].dt.isocalendar().week

    # Add a column for the quarter
    df['QUARTER'] = df['DATE'].dt.quarter

    # Add a column for the season
    df['SEASON'] = (df['DATE'].dt.month % 12 + 3) // 3
    season_map = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}
    df['SEASON'] = df['SEASON'].map(season_map)

    # Add columns for lagged versions of the climate variables
    for var in climate_vars:
        for i in range(1, 31):
            df[f'{var}_lag_{i}'] = df[var].shift(i)

    # Add columns for the mean over a 5-day window for each climate variable
    # based on the values of this window last year
    for var in climate_vars:
        df[f'{var}_mean_5d_window'] = df[var].shift(365).rolling(window=5).mean()

    return df

if __name__ == "__main__":
    # create the output directory if it doesn't exist
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    for file in noaa_files:
        engineered_data = feature_engineering_noaa_climate_data(os.path.join(noaa_data_path, file))
        # Save the feature-engineered data to a new CSV file
        engineered_data.to_csv(f"{out_path}/{file}", index=False)


