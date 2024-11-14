# base model: Random Forest
# for each weather station, we train a separate base model that predicts TMIN, TMAX, and TAVG
# hyperparameters are tuned by cross-validation

import numpy as np
from sklearn.ensemble import RandomForestRegressor

class RandomForest:
    def __init__(self, n_estimators: int  =100, min_samples_leaf: int = 1, max_features: str = None) -> None:
        """
        initialize the model
        :param n_estimators: number of trees in the forest
        :param min_samples_leaf: minimum number of samples required to be at a leaf node
        :param max_features: number of features to consider when looking for the best split
        """
        self.n_estimators = n_estimators
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.model = RandomForestRegressor(n_estimators=self.n_estimators,
                                           min_samples_leaf=self.min_samples_leaf,
                                           max_features=self.max_features)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        fit the model that predicts the 3 target variables
        :param X: array-like of shape (n_samples, n_features)
        :param y: array-like of shape (n_samples, 3)
        :return: None
        """
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        predict the target
        :param X: array-like of shape (n_samples, n_features)
        :return: array-like of shape (n_samples,)
        """
        return self.model.predict(X)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        return the MSE of the model on the given data
        :param X: array-like of shape (n_samples, n_features)
        :param y: array-like of shape (n_samples,)
        :return: float
        """
        return np.mean((self.predict(X) - y) ** 2)

    def get_params(self) -> dict:
        """
        get the model parameters
        :return: dict
        """
        return self.model.get_params()

    def set_params(self, **params) -> 'RandomForest':
        """
        set model parameters
        :param params: dict
        :return: RandomForest
        """
        self.model.set_params(**params)
        return self