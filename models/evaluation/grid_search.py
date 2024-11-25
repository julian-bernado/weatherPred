# Import necessary packages
import os
import itertools
import random
import time
import numpy as np
import pandas as pd

# Import functions from this repo
from models.evaluation.cross_validation import cv_slide
from models.utils import folder_to_data_dict
from models.model import MultiStationModel

# Set Seed
random.seed(604)

# Define relevant file paths
in_data_filepath = os.path.join(os.path.dirname(__file__), "../../data/processed_data")
out_csv_filepath = os.path.join(os.path.dirname(__file__), "evaluation_results/")
out_model_filepath = os.path.join(os.path.dirname(__file__), "../../saved_models/")

# Extract files
files = os.listdir(in_data_filepath)
files = [os.path.join(in_data_filepath, f) for f in files if f.endswith(".csv")]
data = folder_to_data_dict(files)

# Define hyperparameter ranges for RF and Ridge

random_forest_hyperparameters = {
    "n_estimators": [100, 150, 200],
    "min_samples_leaf": [2, 5, 10],
    "max_features": ["sqrt"]
}

ridge_hyperparameters = {
    "alpha": [10 ** i for i in np.linspace(-3, 8, 20)]
}

gp_hyperparameters = {
    "length_scale": [1, 10],
    "sigma": [1],
    "kernel": ["rbf", "matern"]
}

random_forest_combinations = list(itertools.product(random_forest_hyperparameters["n_estimators"],
                                                    random_forest_hyperparameters["min_samples_leaf"],
                                                    random_forest_hyperparameters["max_features"]))

gp_combinations = list(itertools.product(gp_hyperparameters["length_scale"],
                                         gp_hyperparameters["sigma"],
                                         gp_hyperparameters["kernel"]))

# Create cross-validation dataframe

random_forest_hyperparameters = pd.DataFrame(list(random_forest_combinations),
                                             columns=["n_estimators", "min_samples_leaf", "max_features"])

ridge_hyperparameters = pd.DataFrame(ridge_hyperparameters["alpha"], columns=["alpha"])

gp_hyperparameters = pd.DataFrame(gp_combinations, columns=["length_scale", "sigma", "kernel"])

if __name__ == "__main__":

    print("Beginning cross validation")
    time1 = time.time()

    # Fill out ridge hyperparameter df and save it
    ridge_hyperparameters["MSE"] = ridge_hyperparameters.apply(
        lambda row: cv_slide(model_name="ridge", hyperparameters=row.to_dict(), cv_length=14),
        axis=1
    )

    ridge_hyperparameters.to_csv(out_csv_filepath + "ridge_hyperparameters.csv")

    # Fill out GP hyperparameter df and save it
    gp_hyperparameters["MSE"] = gp_hyperparameters.apply(
        lambda row: cv_slide(model_name="gaussian_process", hyperparameters=row.to_dict(), cv_length=1),
        axis=1
    )
    gp_hyperparameters.to_csv(out_csv_filepath + "gp_hyperparameters.csv")


    # Fill out random forest hyperparameter df and save it
    random_forest_hyperparameters["MSE"] = random_forest_hyperparameters.apply(
        lambda row: cv_slide(model_name="random_forest", hyperparameters=row.to_dict(), cv_length=14),
        axis=1
    )

    random_forest_hyperparameters.to_csv(out_csv_filepath + "random_forest_hyperparameters.csv")

    # Extract rows corresponding to minimum MSE for each method
    min_random_forest = random_forest_hyperparameters.loc[random_forest_hyperparameters["MSE"].idxmin()].to_dict()
    min_ridge = ridge_hyperparameters.loc[ridge_hyperparameters["MSE"].idxmin()].to_dict()
    min_gp = gp_hyperparameters.loc[gp_hyperparameters["MSE"].idxmin()].to_dict()

    # Define the correct final model
    print(f"Best RF MSE: {min_random_forest['MSE']}")
    print(f"Best Ridge MSE: {min_ridge['MSE']}")
    print(f"Best GP MSE: {min_gp['MSE']}")
    min_mse = min(min_random_forest["MSE"], min_ridge["MSE"], min_gp["MSE"])
    if min_mse == min_random_forest["MSE"]:
        final_model = MultiStationModel(model_name="random_forest",
                                        n_estimators=min_random_forest["n_estimators"],
                                        min_samples_leaf=min_random_forest["min_samples_leaf"],
                                        max_features=min_random_forest["max_features"])
        print(f"Best model is RF(n_estimators = {min_random_forest['alpha']}, min_samples_leaf = {min_random_forest['min_samples_leaf']}, max_features = {min_random_forest['max_features']})")
    elif min_mse == min_ridge["MSE"]:
        final_model = MultiStationModel(model_name="ridge",
                                        alpha=min_ridge["alpha"])
        print(f"Best model is Ridge(alpha = {min_ridge['alpha']}")
    else:
        final_model = MultiStationModel(model_name="gaussian_process",
                                        alpha=min_gp["alpha"],
                                        kernel=min_gp["kernel"])
        print(f"Best model is GP(alpha = {min_gp['alpha']}, kernel = {min_gp['kernel']})")

    print(f"model search complete in {time.time() - time1} seconds")
    # Fit the final model
    final_model.fit(data)
    final_model.save(out_model_filepath + "final_model.pkl")
