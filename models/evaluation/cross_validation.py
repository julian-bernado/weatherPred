import os
import numpy as np
from models.utils import folder_to_data_dict
from models.model import MultiStationModel

# get current path, move up one directory, and then into the data folder
in_data_filepath = os.path.join(os.path.dirname(__file__), "../../data/processed_data")
# get current path, move up one directory, and then into the saved_models folder
out_model_filepath = os.path.join(os.path.dirname(__file__), "../../saved_models/")

# get the list of files in the data folder
files = os.listdir(in_data_filepath)
# remove any non-csv files and join the file names with the path
files = [os.path.join(in_data_filepath, f) for f in files if f.endswith(".csv")]
# construct the data dictionary
data = folder_to_data_dict(files)


def sequential_cv(model_name, hyperparameters, shift) -> float:
    """
    Function to train a model with a sequential cross-validation
    """
    print("hyperparameters")
    print(hyperparameters)
    train_data = {}
    test_data = {}
    for station in data:
        X, y = data[station]
        # get the all but the last 5 rows of the data
        if shift == 0:
            X_train = X.iloc[:-5]
            y_train = y.iloc[:-5]
            X_eval = X.iloc[-5:]
            y_eval = y.iloc[-5:]
        else:
            X_train = X.iloc[:-(5 + shift)]
            y_train = y.iloc[:-(5 + shift)]
            X_eval = X.iloc[-(5 + shift):-shift]
            y_eval = y.iloc[-(5 + shift):-shift]

        # add to the training data
        train_data[station] = (X_train, y_train)
        # add to the evaluation data
        test_data[station] = (X_eval, y_eval)

    # initialize the model
    if model_name == "random_forest":
        model = MultiStationModel(model_name="random_forest",
                                  n_estimators=hyperparameters["n_estimators"],
                                  min_samples_leaf=hyperparameters["min_samples_leaf"],
                                  max_features=hyperparameters["max_features"])
    elif model_name == "ridge":
        model = MultiStationModel(model_name="ridge",
                                  alpha=hyperparameters["alpha"])
    elif model_name == "gaussian_process":
        model = MultiStationModel(model_name="gaussian_process",
                                  length_scale=hyperparameters["length_scale"],
                                  sigma=hyperparameters["sigma"],
                                  kernel=hyperparameters["kernel"])
    else:
        raise Exception("Invalid model name")

    model.fit(train_data)
    return model.evaluate(test_data)


def cv_slide(model_name, hyperparameters, cv_length):
    """
    Averages CV across the right set of days
    """
    sliding_mse = [sequential_cv(model_name, hyperparameters, shift=i) for i in range(cv_length)]
    return np.mean(sliding_mse).item()
