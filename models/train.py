# implements the training loop for the model
# takes in data files and model hyperparameters
# trains the model and saves it to disk

import os
from models.utils import folder_to_data_dict
from models.model import MultiStationModel

# get current path, move up one directory, and then into the data folder
in_data_filepath = os.path.join(os.path.dirname(__file__), "../data/processed_data")
# get current path, move up one directory, and then into the saved_models folder
out_model_filepath = os.path.join(os.path.dirname(__file__), "../saved_models/")


if __name__ == "__main__":
    # get the list of files in the data folder
    files = os.listdir(in_data_filepath)
    # remove any non-csv files and join the file names with the path
    files = [os.path.join(in_data_filepath, f) for f in files if f.endswith(".csv")]
    # construct the data dictionary
    data = folder_to_data_dict(files)

    # construct train and test data
    train_data = {}
    test_data = {}
    for station in data:
        X, y = data[station]
        # get the all but the last 5 rows of the data
        X_train = X.iloc[:-5]
        y_train = y.iloc[:-5]
        # get the last 5 rows of the data
        X_eval = X.tail(5)
        y_eval = y.tail(5)
        # add to the training data
        train_data[station] = (X_train, y_train)
        # add to the evaluation data
        test_data[station] = (X_eval, y_eval)

    # initialize the model
    model = MultiStationModel(model_name="random_forest", n_estimators=100, min_samples_leaf=2, max_features=None)
    # fit the model to the data
    model.fit(train_data)
    # evaluate the model
    mse = model.evaluate(test_data)
    print(f"Mean squared error: {mse}")
    # save the model to disk
    model.save(os.path.join(out_model_filepath, "model.pkl"))