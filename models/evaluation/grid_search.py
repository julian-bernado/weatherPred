# Import necessary packages
import os
import itertools
import random
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
    "n_estimators": [100, 150, 200, 250, 300, 350, 400],
    "min_samples_leaf": [2, 5, 10, 20],
    "max_features": ["sqrt", "log2"]
}

ridge_hyperparameters = {
    "alpha": [10 ** i for i in np.linspace(-5, 5, 20)]
}

random_forest_combinations = list(itertools.product(random_forest_hyperparameters["n_estimators"],
                                                    random_forest_hyperparameters["min_samples_leaf"],
                                                    random_forest_hyperparameters["max_features"]))

# Create cross-validation dataframe

random_forest_hyperparameters = pd.DataFrame(list(random_forest_combinations),
                                             columns=["n_estimators", "min_samples_leaf", "max_features"])

ridge_hyperparameters = pd.DataFrame(ridge_hyperparameters["alpha"], columns=["alpha"])

if __name__ == "__main__":

    # Fill out ridge hyperparameter df and save it
    ridge_hyperparameters["MSE"] = ridge_hyperparameters.apply(
        lambda row: cv_slide(model_name="ridge", hyperparameters=row.to_dict(), cv_length=2),
        axis=1
    )

    ridge_hyperparameters.to_csv(out_csv_filepath + "ridge_hyperparameters.csv")

    # Fill out random forest hyperparameter df and save it
    random_forest_hyperparameters["MSE"] = random_forest_hyperparameters.apply(
        lambda row: cv_slide(model_name="random_forest", hyperparameters=row.to_dict(), cv_length=2),
        axis=1
    )

    random_forest_hyperparameters.to_csv(out_csv_filepath + "random_forest_hyperparameters.csv")

    # Extract rows corresponding to minimum MSE for each method
    min_random_forest = random_forest_hyperparameters.loc[random_forest_hyperparameters["MSE"].idxmin()].to_dict()
    min_ridge = ridge_hyperparameters.loc[ridge_hyperparameters["MSE"].idxmin()].to_dict()

    # Define the correct final model
    if min_random_forest["MSE"] < min_ridge["MSE"]:
        final_model = MultiStationModel(model_name="random_forest",
                                        n_estimators=min_random_forest["n_estimators"],
                                        min_samples_leaf=min_random_forest["min_samples_leaf"],
                                        max_features=min_random_forest["max_features"])
    else:
        final_model = MultiStationModel(model_name="ridge",
                                        alpha=min_ridge["alpha"])

    # Fit the final model
    final_model.fit(data)
    final_model.save(out_model_filepath + "final_model.pkl")
