import pandas as pd


def folder_to_data_dict(filepaths: list) -> dict:
    data = {}
    for f in filepaths:
        # read in the data
        df = pd.read_csv(f)
        # get the station id: filename is of the form "weatherPred/models/../data/processed_data/KPWM.csv"
        station = f.split("/")[-1].split(".")[0]
        # drop the TMIN, TMAX, and TAVG columns
        X = df.drop(columns=["TMIN", "TMAX", "TAVG"])
        # get the target variables
        y = df[["TMIN", "TMAX", "TAVG"]]
        # add the data to the dictionary
        data[station] = (X, y)
    return data