# implements the training loop for the model
# takes in data files and model hyperparameters
# trains the model and saves it to disk

import os
from models.utils import folder_to_data_dict
from models.model import MultiStationModel
import time

# get current path, move up one directory, and then into the data folder
in_data_filepath = os.path.join(os.path.dirname(__file__), "../data/processed_data")
# get current path, move up one directory, and then into the saved_models folder
out_model_filepath = os.path.join(os.path.dirname(__file__), "../saved_models/")


if __name__ == "__main__":
    train_flag = True

    # get the list of files in the data folder
    files = os.listdir(in_data_filepath)
    # remove any non-csv files and join the file names with the path
    files = [os.path.join(in_data_filepath, f) for f in files if f.endswith(".csv")]
    print(files)
    # construct the data dictionary
    data = folder_to_data_dict(files)
    print(data.keys())

    # construct train and test data
    train_data = {}
    test_data = {}
    last_day_X ={}
    last_day_y = {}
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
        # add to the last day data
        last_day_X[station] = X.tail(1)
        last_day_y[station] = y.tail(1).to_numpy().flatten()

    # train the model
    if train_flag:
        # initialize the model
        model = MultiStationModel(model_name="random_forest", n_estimators=100, min_samples_leaf=2, max_features=None)
        # time to fit the model
        start_time = time.time()
        # fit the model to the data
        model.fit(train_data)
        print(f"Model fitting took {time.time() - start_time} seconds")
    else:
        # load the model from disk
        model = MultiStationModel.load(os.path.join(out_model_filepath, "model.pkl"))
    # evaluate the model
    mse = model.evaluate(test_data)
    print(f"Mean squared error: {mse}")
    # predict the last day
    predictions = model.predict(last_day_X)
    # print difference between predictions and actual values
    for station in predictions:
        print(f"Station: {station} \n"
              f"Predicted - Actual: {predictions[station] - last_day_y[station]}")
    # save theR model to disk
    model.save(os.path.join(out_model_filepath, "model.pkl"))