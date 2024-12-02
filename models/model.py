# class that takes a model from modules folder and creates a
# model object that consists of multiple base models one for each weather station

import numpy as np
from models.modules.ridge_regression import RidgeRegressor
from models.modules.random_forest import RandomForest
from models.modules.gaussian_process import GaussianProcess
import pickle
import time

class MultiStationModel:
    def __init__(self, model_name: str, **kwargs) -> None:
        """
        Initialize the model
        :param model_name: name of the submodel
        :param kwargs: dictionary of model parameters
        """
        self.model_name = model_name
        self.models = {}
        self.kwargs = kwargs

    def fit(self, data: dict, verbose: bool = True) -> None:
        """
        Fit the submodels to the data
        :param verbose:
        :param data: dictionary of tuples {station_s: (X_s, y_s) for s in stations}
        :return: None
        """
        for station, (X, y) in data.items():
            if self.model_name == 'ridge':
                station_model = RidgeRegressor(**self.kwargs)
            elif self.model_name == 'random_forest':
                station_model = RandomForest(**self.kwargs)
            elif self.model_name == 'gaussian_process':
                station_model = GaussianProcess(**self.kwargs)
            else:
                raise ValueError('Invalid name')
            # time to fit the model
            start_time = time.time()
            station_model.fit(X, y)
            if verbose:
                print(f"{self.model_name} Model for station {station} fitted in {time.time() - start_time} seconds")
            self.models[station] = station_model

    def predict(self, X: dict) -> dict:
        """
        Predict the target for each station
        :param X: dictionary of input data {station_s: X_s for s in stations}
        :return y_pred: dictionary of predictions {station_s: y_pred_s for s in stations}
        """
        y_pred = {}
        for station, model in self.models.items():
            y_pred[station] = model.predict(X[station])
        return y_pred

    def evaluate(self, data: dict) -> float:
        """
        Evaluate the model on the given data
        :param data: dictionary of tuples {station_s: (X_s, y_s) for s in stations}
        :return: mean squared error of the model on the given data
        """
        errors = []
        for station, (X, y) in data.items():
            errors.append(self.models[station].evaluate(X, y))
        return np.mean(errors).item()

    def get_params(self) -> dict:
        """
        Get the model parameters
        :return: dictionary of model parameters
        """
        return self.kwargs

    def set_params(self, **params) -> 'MultiStationModel':
        """
        Set model parameters
        :param params: dictionary of model parameters
        :return: self
        """
        self.kwargs = params
        return self

    def save(self, path: str) -> None:
        """
        Save the model to a file
        :param path: path to the file
        :return: None
        """
        with open(path, 'wb') as f:
            # noinspection PyTypeChecker
            pickle.dump(self, f)

    @staticmethod
    def load(path: str) -> 'MultiStationModel':
        """
        Load the model from a file
        :param path: path to the file
        :return: model object
        """
        with open(path, 'rb') as f:
            return pickle.load(f)
