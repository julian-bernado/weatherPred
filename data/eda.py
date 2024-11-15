# import libraries
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import correlate

# relative file path to the processed data
noaa_data_path = os.path.join(os.path.dirname(__file__), '../data/raw_data/noaa/to_csv')
noaa_files = os.listdir(noaa_data_path)

# function to perform EDA on the NOAA GHCN-DAILY climate dataset.
def eda_noaa_climate_data(file_path: str):
    """
    :param file_path: Path to the CSV file containing the climate data for a specific city.
    :returns: None
    """
    ### Processing
    # Extract the city code
    city_code = os.path.splitext(os.path.basename(file_path))[0]
    
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

    ### Summary statistics
    print("Basic Information:")
    print(df.info())
    print("\nSummary Statistics:")
    print(df.describe())

    ### Missing data analysis
    # Check for missing proportion of missing values by column
    print("\nMissing Values:")
    print(df.isnull().mean())
    
    # Add year, month columns for plotting
    df['YEAR'] = df['DATE'].dt.year
    df['MONTH'] = df['DATE'].dt.month 
    
    # Plot patterns in missingness over time
    missing_by_year = df.groupby('YEAR').apply(lambda x : x.isna().mean(), include_groups=False).drop(['MONTH'], axis=1)
    missing_by_year.plot(kind='line', marker='o', figsize=(10, 6))
    plt.xlabel('Year')
    plt.ylabel('Proportion of Missing Values')
    plt.title(f'Proportion of Missing Values by Year ({city_code})')
    plt.legend(title='Columns')
    plt.grid()
    #os.makedirs('data/plots/missing_time/', exist_ok=True)
    #plt.savefig(f'data/plots/missing_time/{city_code}_missing_time_plt.png', format='png', dpi=300)


    ### Time series trend analysis
    # Daily time series plot for each climate variable
    for var in climate_vars:
        plt.figure(figsize=(15, 6))
        plt.plot(df['DATE'], df[var])
        plt.title(f'Time-Series Plot of {var} ({city_code})')
        plt.xlabel('Date')
        plt.ylabel(var)
        #os.makedirs('data/plots/climate_time/', exist_ok=True)
        #plt.savefig(f'data/plots/climate_time/{var}_{city_code}_daily_plt.png', format='png', dpi=300)

    # Monthly series plot for each climate variable
    df_monthly_avg = df.groupby('MONTH')[climate_vars + ['MONTH']].apply(lambda x : x.mean())
    for var in climate_vars:
        plt.figure(figsize=(15, 6))
        plt.plot(df_monthly_avg['MONTH'], df_monthly_avg[var])
        plt.title(f'Time-Series Plot of {var} ({city_code})')
        plt.xlabel('Month')
        plt.ylabel(var)
        #os.makedirs('data/plots/climate_time/', exist_ok=True)
        #plt.savefig(f'data/plots/climate_time/{var}_{city_code}_monthly_plt.png', format='png', dpi=300)

    # Yearly series plot for each climate variable
    df_yearly_avg = df.groupby('YEAR')[climate_vars + ['YEAR']].apply(lambda x : x.mean())
    for var in climate_vars:
        plt.figure(figsize=(15, 6))
        plt.plot(df_yearly_avg['YEAR'], df_yearly_avg[var])
        plt.title(f'Time-Series Plot of {var} ({city_code})')
        plt.xlabel('Year')
        plt.ylabel(var)
        #os.makedirs('data/plots/climate_time/', exist_ok=True)
        #plt.savefig(f'data/plots/climate_time/{var}_{city_code}_yearly_plt.png', format='png', dpi=300)

    ### Cross-correlation analysis
    # Cross-correlation matrix for all pairs of climate variables
    # We ignore TAVG for now because of NAs
    df_sub = df[['PRCP', 'TMIN', 'TMAX']].dropna()
    cross_cov_dict = {}
    max_lag = 30
    for col1 in df_sub.columns:
        for col2 in df_sub.columns:
            cross_covs = [correlate(df_sub[col1] - df_sub[col1].mean(), df_sub[col2] - df_sub[col2].mean(), mode='full')[len(df_sub) - 1 - lag] 
                           for lag in range(max_lag + 1)]
            cross_covs = [c / len(df) for c in cross_covs]  
            cross_cov_dict[(col1, col2)] = cross_covs
    cross_cor_df = pd.DataFrame(cross_cov_dict, index=range(max_lag + 1)).T
    # Normalize by covariances to convert cross-covariance to cross-correlation
    cov = [cross_cor_df.iloc[0,0], cross_cor_df.iloc[4,0], cross_cor_df.iloc[8,0]]
    for i in range(cross_cor_df.shape[0]):
        cross_cor_df.iloc[i] = cross_cor_df.iloc[i] / np.sqrt(cov[i // 3] * cov[((i+1) % 3) - 1])         
    cross_cor_df = cross_cor_df.round(2)
    cross_cor_df.columns = [f'{i}' for i in range(max_lag + 1)]
    plt.figure(figsize=(18, 6))
    sns.heatmap(cross_cor_df, annot=True, cmap="coolwarm", center=0)
    plt.title(f'Cross-Correlation between Variables with Lags ({city_code})')
    plt.xlabel('Lag')
    plt.ylabel('Variables')
    #os.makedirs('data/plots/cross_corr/', exist_ok=True)
    #plt.savefig(f'data/plots/cross_corr/{city_code}_cross_cor.png', format='png', dpi=300)


    print("EDA complete.")

if __name__ == '__main__':
    for file in noaa_files:
        # Run EDA for each file if does not contain 'stations' in the name
        if not 'stations' in file:
            print(f"Running EDA for {file}")
            eda_noaa_climate_data(os.path.join(noaa_data_path, file))


