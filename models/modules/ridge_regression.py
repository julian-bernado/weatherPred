# base model: Ridge Regression
# for each weather station, we train a separate base model
# hyperparameter alpha is tuned by cross-validation

import numpy as np
from sklearn.linear_model import Ridge

class RidgeRegressor:
    def __init__(self, alpha: float = 1.0) -> None:
        """
        initialize the model
        :param alpha: regularization strength
        """
        self.alpha = alpha
        self.model = Ridge(alpha=self.alpha)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        fit the model
        :param X: array-like of shape (n_samples, n_features)
        :param y: array-like of shape (n_samples,)
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

    def set_params(self, **params) -> 'RidgeRegressor':
        """
        set model parameters
        :param params: dict
        :return:
        """
        self.model.set_params(**params)
        return self