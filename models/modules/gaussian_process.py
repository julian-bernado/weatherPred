# base model: Gaussian Process Regression
# for each weather station, we train a separate base model that predicts 5 days of TMIN, TMAX, and TAVG
# hyperparameter length_scale and noise_level are tuned by cross-validation
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, Matern, Sum

class GaussianProcess:
    def __init__(self, kernel: str = 'rbf', length_scale: float = 1.0, sigma: float = 10e-6) -> None:
        """
        initialize the model
        :param kernel: kernel function
        :param length_scale: length scale
        :param sigma: noise level
        """
        self.kernel = kernel
        self.sigma = sigma
        self.length_scale = length_scale
        if self.kernel == 'rbf':
            sum_kernel = Sum(RBF(self.length_scale), WhiteKernel(noise_level=self.sigma))
            self.model = GaussianProcessRegressor(kernel=sum_kernel)
        elif self.kernel == 'matern':
            sum_kernel = Sum(Matern(length_scale=self.length_scale), WhiteKernel(noise_level=self.sigma))
            self.model = GaussianProcessRegressor(kernel=sum_kernel)
        else:
            raise ValueError('Invalid kernel function')

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        fit the model that predicts the 15 target variables
        :param X: array-like of shape (n_samples, n_features)
        :param y: array-like of shape (n_samples, 15)
        :return: None
        """
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        predict the target
        :param X: array-like of shape (n_samples, n_features)
        :return: array-like of shape (n_samples, 15)
        """
        # round to 2 decimal places
        return self.model.predict(X).round(2)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        return the MSE of the model on the given data
        :param X: array-like of shape (n_samples, n_features)
        :param y: array-like of shape (n_samples, 15)
        :return: float
        """
        return np.mean((self.predict(X) - y) ** 2).item()

    def get_params(self) -> dict:
        """
        get the model parameters
        :return: dict
        """
        return self.model.get_params()

    def set_params(self, **params) -> 'GaussianProcess':
        """
        set model parameters
        :param params: dict
        :return: GaussianProcess
        """
        self.model.set_params(**params)
        return self