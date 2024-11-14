# implements the training loop for the model
# takes in data files and model hyperparameters
# trains the model and saves it to disk

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from models.model import MultiStationModel

# get current path, move up one directory, and then into the data folder
in_data_filepath = os.path.join(os.path.dirname(__file__), "../data/processed_data")
# get current path, move up one directory, and then into the saved_models folder
out_model_filepath = os.path.join(os.path.dirname(__file__), "../saved_models/")

# function to construct data structure for the model
# takes in list of files and returns a dictionary of data {station: (X, y) for station in stations}
def folder_to_data_dict(files: list) -> dict:
    data = {}
    for f in files:
        # read in the data
        df = pd.read_csv(os.path.join(in_data_filepath, f))
        # get the station id: filename is of the form "station_id.csv"
        station = f.split(".")[0]
        # drop the TMIN, TMAX, and TAVG columns
        X = df.drop(columns=["TMIN", "TMAX", "TAVG"])
        # get the target variables
        y = df[["TMIN", "TMAX", "TAVG"]]
        # add the data to the dictionary
        data[station] = (X, y)
    return data


if __name__ == "__main__":
    # get the list of files in the data folder
    files = os.listdir(in_data_filepath)
    # construct the data dictionary
    data = folder_to_data_dict(files)

    # initialize the model
    model = MultiStationModel(model_name="random_forest", n_estimators=100, min_samples_leaf=2, max_features=None)
    # fit the model to the data
    model.fit(data)
    # save the model to disk
    model.save(os.path.join(out_model_filepath, "model.pkl"))