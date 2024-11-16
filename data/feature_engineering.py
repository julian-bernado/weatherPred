# import libraries
import os
import pandas as pd
from datetime import datetime, timedelta


# relative file path to the processed data
noaa_data_path = os.path.join(os.path.dirname(__file__), 'raw_data/noaa/to_csv')
out_path = os.path.join(os.path.dirname(__file__), 'processed_data')
noaa_files = os.listdir(noaa_data_path)

# function to perform feature engineering on each city's NOAA climate dataset that was converted to .csv.
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
    weather_gov_file_path = file_path.replace('noaa', 'weather_gov')
    weather_gov_df = feature_engineering_weather_gov_data(weather_gov_file_path)

    # Combine the two datasets
    df = pd.concat([noaa_df, weather_gov_df], axis=0)

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

# function to perform feature engineering on each city's weather.gov climate dataset that was converted to .csv.
def feature_engineering_weather_gov_data(file_path: str) -> pd.DataFrame:
    """
    :param file_path: Path to the CSV file containing the weather.gov climate data for a specific city.
    :returns: A pandas DataFrame with the feature-engineered climate data.
    """
    # Load the dataset
    df = pd.read_csv(file_path)

    # Filter out today's calendar date due to data incompleteness
    df = df[df['Date'] < pd.Timestamp.now().day]
    df.rename(columns={'Date': 'DATE'}, inplace=True)

    # Compute daily aggregated (daily min, max, avg) temperature values and aggregate precipitation
    df_daily = df.groupby('DATE').agg(
        PRCP=('Precipitation (in) 1 hr', 'sum'),
        TMIN=('Temperature (ÂºF) Air', 'min'),
        TAVG=('Temperature (ÂºF) Air', 'mean'),
        TMAX=('Temperature (ÂºF) Air', 'max')
    ).reset_index()

    # Convert aggregate precipitation from in to tenths of mm
    df_daily['PRCP'] = df_daily['PRCP'] * 254

    # Convert date column to datetime based on stored value of day of month and current calendar date
    current_year = datetime.now().year
    current_month = datetime.now().month
    df_daily['DATE'] = df_daily['DATE'].apply(lambda x: datetime(current_year, current_month, x))

    return df_daily


if __name__ == "__main__":
    # create the output directory if it doesn't exist
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    for file in noaa_files:
        # Skip the stations file
        if not 'stations' in file:
            # Perform feature engineering on the climate data
            engineered_data = feature_engineering_noaa_climate_data(os.path.join(noaa_data_path, file))
            # Save the feature-engineered data to a new CSV file
            engineered_data.to_csv(f"{out_path}/{file}", index=False)
