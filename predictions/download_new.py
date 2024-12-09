# Script to download, process, and combine weather_gov data with existing NOAA data

from data.scraper import weather_gov_scraper
from data.converter import html_to_csv
from data.feature_engineering import feature_engineering_weather_gov_data

import os
import requests
import pandas as pd
from datetime import datetime, timedelta


def feature_engineering_noaa_climate_data(file_path: str) -> pd.DataFrame:
    """
    :param file_path: Path to the CSV file containing the climate data for a specific city.
    :returns: A pandas DataFrame with the feature-engineered climate data.
    """
    # Load the NOAA dataset
    noaa_df = pd.read_csv(file_path, parse_dates=['DATE'])

    # Filter out today and prior 2 days of data due to incompleteness
    # We will augment it with the weather.gov dataset
    noaa_df = noaa_df[noaa_df['DATE'] < (pd.Timestamp.now() - timedelta(days=4))]

    # Climate variables of interest
    climate_vars = ['PRCP', 'TMIN', 'TAVG', 'TMAX']
    noaa_df = noaa_df[['DATE'] + climate_vars]

    # Convert temperature variables from tenths of a degree Celsius to Farenheit
    # (see NOAA docs: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt)
    noaa_df['TMIN'] = noaa_df['TMIN'] / 10 * (9 / 5) + 32
    noaa_df['TAVG'] = noaa_df['TAVG'] / 10 * (9 / 5) + 32
    noaa_df['TMAX'] = noaa_df['TMAX'] / 10 * (9 / 5) + 32

    # Load the weather.gov dataset, which is already measured in Farenheit
    weather_gov_file_path = "predictions/new_data/to_csv/"
    station = file_path[-8:]
    weather_gov_df = feature_engineering_weather_gov_data(weather_gov_file_path + station)
    print("weather gov")
    print(weather_gov_df.tail(1))
    print("noaa")
    print(noaa_df.tail(1))

    # Combine the two datasets
    df = pd.concat([noaa_df, weather_gov_df], axis=0)
    print("df")
    print(df.tail(1))

    # Add year, month columns for plotting
    df['YEAR'] = df['DATE'].dt.year
    # Drop all observations before Year 2013
    df = df[df['YEAR'] >= 2013]
    df['MONTH'] = df['DATE'].dt.month

    # Add a column for the day of the year
    df['DAY_OF_YEAR'] = df['DATE'].dt.dayofyear

    # Add a column for the week of the year
    df['WEEK_OF_YEAR'] = df['DATE'].dt.isocalendar().week

    # Add a column for the season
    # season_map = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}
    df['SEASON'] = (df['DATE'].dt.month % 12 + 3) // 3

    # Add columns for lagged versions of the climate variables
    for var in climate_vars:
        # Create a dictionary of forward and backward lagged columns
        # Forward lags are for multi-day out prediction, backward lags are predictors
        backward_lagged_columns = {f'{var}_lag_{i}': df[var].shift(i) for i in range(1, 30 + 1)}
        forward_lagged_columns = {f'{var}_lag_{i}': df[var].shift(i) for i in range(-1, -4 - 1, -1)}
        # Convert dictionaries to DataFrame and concatenate
        backward_lagged_df = pd.DataFrame(backward_lagged_columns)
        forward_lagged_df = pd.DataFrame(forward_lagged_columns)
        df = pd.concat([df, backward_lagged_df, forward_lagged_df], axis=1)

    # Add columns for the mean over a 5-day window for each climate variable
    # based on the values of this window last year
    for var in climate_vars:
        df[f'{var}_mean_5d_window'] = df[var].shift(365).rolling(window=5).mean()

    # Drop date column and convert all values in the df to float
    df = df.drop('DATE', axis=1).astype(float)

    # Drop all observations with missing values
    df = df.dropna()

    # Re-order columns so today's climate variables and negative lags are at the beginning
    df = df[[item for sublist in [
        ['TMIN', 'TMAX', 'TAVG'],  # Basic variables
        *[
            [f'TMIN_lag_{i}', f'TAVG_lag_{i}', f'TMAX_lag_{i}']
            for i in range(-1, -5, -1)
        ],  # Negative lags
        *[
            [f'TMIN_lag_{i}', f'TAVG_lag_{i}', f'TMAX_lag_{i}', f'PRCP_lag_{i}']
            for i in range(1, 31)
        ],  # Positive lags
        [
            f'{var}_mean_5d_window' for var in climate_vars
        ],  # Mean window variables
        ['YEAR', 'MONTH', 'DAY_OF_YEAR', 'WEEK_OF_YEAR', 'SEASON'],  # Time features
    ] for item in sublist]]

    return df


weather_gov_raw_path = os.path.join(os.path.dirname(__file__), "new_data")
weather_gov_converted_path = os.path.join(os.path.dirname(__file__), "new_data/to_csv")
weather_gov_processed_path = os.path.join(os.path.dirname(__file__), "new_data/processed")
noaa_converted_file_path = os.path.join(os.path.dirname(__file__), "../data/raw_data/noaa/to_csv")
noaa_files = os.listdir(noaa_converted_file_path)

# create the output directory if it doesn't exist
if not os.path.exists(weather_gov_raw_path):
    os.makedirs(weather_gov_raw_path)

if not os.path.exists(weather_gov_converted_path):
    os.makedirs(weather_gov_converted_path)

if not os.path.exists(weather_gov_processed_path):
    os.makedirs(weather_gov_processed_path)

if __name__ == "__main__":
    weather_gov_scraper(weather_gov_raw_path, verbose=True)
    for file in os.listdir(weather_gov_raw_path):
        # skip the file if it is a directory
        if os.path.isdir(f"{weather_gov_raw_path}/{file}"):
            continue
        # if the file is .html file
        elif file.endswith(".html"):
            # read the file
            data = html_to_csv(f"{weather_gov_raw_path}/{file}")
            # save the file to csv format
            data.to_csv(f"{weather_gov_converted_path}/{file.replace('.html', '.csv')}", index=False)

    for file in noaa_files:
        print(f"Processing {file}")
        # Skip the stations file
        if 'stations' not in file:
            # Perform feature engineering on the climate data
            engineered_data = feature_engineering_noaa_climate_data(os.path.join(noaa_converted_file_path, file))
            # Save the feature-engineered data to a new CSV file
            engineered_data.to_csv(f"{weather_gov_processed_path}/{file}", index=False)
