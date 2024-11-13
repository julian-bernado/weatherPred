# base model: Ridge Regression
# for each weather station, we train a separate base model
# the hyperparameter alpha is tuned by cross-validation

import numpy as np
from sklearn.linear_model import Ridge

class RidgeRegressor:
    # initialize the model
    def __init__(self, alpha: float = 1.0) -> None:
        self.alpha = alpha
        self.model = Ridge(alpha=self.alpha)

    # fit the model
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)

    # predict the target
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    # evaluate the model
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        # return the R^2 score
        return self.model.score(X, y)

    # get the hyperparameter alpha
    def get_params(self) -> dict:
        return self.model.get_params()

    # set the hyperparameter alpha
    def set_params(self, **params) -> None:
        self.model.set_params(**params)
        return