import pandas as pd


def folder_to_data_dict(filepaths: list) -> dict:
    """
    Read in the data from the given list of filepaths and return a dictionary.
    Targets are in the first 15 columns and features are in the rest
    :param filepaths: list of filepaths of station datasets
    :return: dictionary of data {station_id: (X, y)}
    """
    data = {}
    for f in filepaths:
        # read in the data
        df = pd.read_csv(f)
        # get the station id: filename is of the form "weatherPred/models/../data/processed_data/KPWM.csv"
        station = f.split("/")[-1].split(".")[0]
        # drop the first 15 columns
        X = df.drop(df.columns[:15], axis=1)
        # get the target variables (first 15 columns)
        y = df[df.columns[:15]]
        # add the data to the dictionary
        data[station] = (X, y)
    return data