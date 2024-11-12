# .dly file format processing

# import libraries
import os
import pandas as pd

# base filepath for the NOAA data
noaa_in_path = os.path.join(os.path.dirname(__file__), "raw_data/noaa")
noaa_out_path = os.path.join(os.path.dirname(__file__), "raw_data/noaa/to_csv")

# data spec from https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt

## STATION_ID: station identification code (11 characters)
## YEAR: year (4 characters)
## MONTH: month (2 characters)
## ELEMENT: indicator of element type (4 characters), e.g. TMAX, TMIN, TAVG, PRCP, ...
data_header_names = [
    "STATION_ID",
    "YEAR",
    "MONTH",
    "ELEMENT"
]
data_header_col_specs = [
    (0,  11),
    (11, 15),
    (15, 17),
    (17, 21)
]
data_header_dtypes = {
    "STATION_ID": "str",
    "YEAR": "int",
    "MONTH": "int",
    "ELEMENT": "str"
}
## VALUEi: data value for day i (5 characters)
## MFLAGi: measurement flag for day i (1 character)
## QFLAGi: quality flag for day i (1 character)
## SFLAGi: source flag for day i (1 character)
data_day_col_names = [
    [
        "VALUE" + str(i + 1),
        "MFLAG" + str(i + 1),
        "QFLAG" + str(i + 1),
        "SFLAG" + str(i + 1)
    ] for i in range(31)
]
# day field width is (5,1,1,1) for each day
data_day_col_specs = [
    [
        (21 + i * 8, 26 + i * 8),
        (26 + i * 8, 27 + i * 8),
        (27 + i * 8, 28 + i * 8),
        (28 + i * 8, 29 + i * 8)
    ] for i in range(31)
]
data_col_dtypes = [
    {
        "VALUE" + str(i + 1): int,
        "MFLAG" + str(i + 1): str,
        "QFLAG" + str(i + 1): str,
        "SFLAG" + str(i + 1): str
    } for i in range(31)
]
# flatten the lists of lists
data_day_col_names = [item for sublist in data_day_col_names for item in sublist]
data_day_col_specs = [item for sublist in data_day_col_specs for item in sublist]
data_dtypes = {**data_header_dtypes, **{k: v for d in data_col_dtypes for k, v in d.items()}}

# function to read a .dly file from NOAA and return a DataFrame
def read_dly_file(file_path: str) -> pd.DataFrame:
    """
    :param file_path: path to the .dly file
    :return: DataFrame with the data
    """
    # read the file
    df = pd.read_fwf(
        file_path,
        colspecs=data_header_col_specs + data_day_col_specs,
        header=None,
        names=data_header_names + data_day_col_names,
        dtype=data_dtypes
    )

    # drop the flags columns
    df.drop(columns=[f for f in df.columns if "FLAG" in f], inplace=True)

    # melt the DataFrame so that each row is a single observation
    df = df.melt(
        id_vars=data_header_names,
        value_vars=[f"VALUE{i}" for i in range(1, 32)],
        var_name="DAY",
        value_name="VALUE"
    )

    # Day column is numeric
    df["DAY"] = df["DAY"].str.extract(r"(\d+)").astype(int)

    # substitute -9999 with NaN
    df.replace(-9999, pd.NA, inplace=True)
    # drop rows with NaN values for datetime
    df.dropna(inplace=True)
    # create a datetime column
    df["DATE"] = pd.to_datetime(df["YEAR"].astype(str) + df["MONTH"].astype(str).str.zfill(2) + df["DAY"].astype(str).str.zfill(2), format="%Y%m%d")
    # pivot the DataFrame, keep station ID, year, month, day, ID, and DATE columns
    df = df.pivot(index=["STATION_ID", "YEAR", "MONTH", "DAY", "DATE"], columns="ELEMENT", values="VALUE").reset_index()
    return df

# Function to process metadata of geolocations of the weather stations
def read_metadata(file_path: str) -> pd.DataFrame:
    """
    :param file_path: path to the .txt file
    :return: DataFrame
    """
    # read the file
    df = pd.read_fwf(
        file_path,
        colspecs=[(0, 11), (12, 20), (21, 30), (31, 37), (38, 40), (41, 71), (72, 75), (76, 79), (80, 85)],
        header=None,
        names=["ID", "LATITUDE", "LONGITUDE", "ELEVATION", "STATE", "NAME", "GSN_FLAG", "HCN_CRN_FLAG", "WMO_ID"]
    )
    # drop the flags columns
    return df[["ID", "LATITUDE", "LONGITUDE", "ELEVATION", "STATE", "NAME"]]


if __name__ == '__main__':
    # create the output directory if it doesn't exist
    if not os.path.exists(noaa_out_path):
        os.makedirs(noaa_out_path)
    # for each file in the noaa directory
    for file in os.listdir(noaa_in_path):
        # skip the file if it is a directory
        if os.path.isdir(f"{noaa_in_path}/{file}"):
            continue
        # if the file is not a .dly (i.e. metadata  txt file)
        elif not file.endswith(".dly"):
            # read the file
            data = read_metadata(f"{noaa_in_path}/{file}")
            # save the file to csv format
            data.to_csv(f"{noaa_out_path}/{file.replace('.txt', '.csv')}", index=False)
            print(f"Converted {file} to {file.replace('.txt', '.csv')}")
        # if the file is a .dly file
        else:
            # read the file
            data = read_dly_file(f"{noaa_in_path}/{file}")
            # save the file to csv format
            data.to_csv(f"{noaa_out_path}/{file.replace('.dly', '.csv')}", index=False)
            print(f"Converted {file} to {file.replace('.dly', '.csv')}")