# predictions.py

import os
import numpy as np
import pandas as pd
from datetime import datetime
from models.utils import folder_to_data_dict
from models.model import MultiStationModel

# Paths
base_dir = os.path.dirname("./")
data_dir = os.path.join(base_dir, 'data', 'processed_data')
model_dir = os.path.join(base_dir, 'saved_models')
model_path = os.path.join(model_dir, 'final_model.pkl')

# Load the pre-trained model
model = MultiStationModel.load(model_path)

# List of station codes in the specified order
stations_order = [
    "PANC",  # Anchorage
    "KBOI",  # Boise
    "KORD",  # Chicago
    "KDEN",  # Denver
    "KDTW",  # Detroit
    "PHNL",  # Honolulu
    "KIAH",  # Houston
    "KMIA",  # Miami
    "KMIC",  # Minneapolis
    "KOKC",  # Oklahoma City
    "KBNA",  # Nashville
    "KJFK",  # New York
    "KPHX",  # Phoenix
    "KPWM",  # Portland ME
    "KPDX",  # Portland OR
    "KSLC",  # Salt Lake City
    "KSAN",  # San Diego
    "KSFO",  # San Francisco
    "KSEA",  # Seattle
    "KDCA",  # Washington DC
]

# Get list of data files
files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]

# Use folder_to_data_dict to get the data
data = folder_to_data_dict(files)

# Prepare to collect all predictions
all_predictions = []

# Current date
current_date = datetime.now().strftime("%Y-%m-%d")

# Iterate over each station in the specified order
for station_code in stations_order:
    if station_code in data:
        X, y = data[station_code]
        # Use the last row of X as features
        X_last = X.tail(1)
        # Check if the model for this station exists
        if station_code in model.models:
            station_model = model.models[station_code]
            # Make prediction
            y_pred = station_model.predict(X_last)
            y_pred = y_pred.flatten()
            y_pred = np.round(y_pred, 1)
            first_avg = y_pred[2]
            first_max = y_pred[1]
            y_pred[1] = first_avg
            y_pred[2] = first_max
            # Collect predictions
            all_predictions.extend(y_pred.tolist())
        else:
            print(f"No model found for station {station_code}")
            # Append NaNs for missing predictions (15 values)
            all_predictions.extend([np.nan] * 15)
    else:
        print(f"No data found for station {station_code}")
        # Append NaNs for missing predictions (15 values)
        all_predictions.extend([np.nan] * 15)

# Check if we have 300 predictions
if len(all_predictions) != 300:
    print(f"Expected 300 predictions, but got {len(all_predictions)}.")

# Format the output
formatted_predictions = ', '.join(f"{num:.1f}" if not np.isnan(num) else "NaN" for num in all_predictions)
output = f'{current_date}, {formatted_predictions}'

# Save the output to a CSV file named "predictions_{date}.csv"
output_csv_filename = f"predictions/intermediate/predictions_{current_date}.csv"
output_csv_path = os.path.join(base_dir, output_csv_filename)
    
# Create a DataFrame for the CSV
# Column names: Date, Pred1, Pred2, ..., Pred300
column_names = ['Date'] + [f'Pred{i+1}' for i in range(300)]
data_row = [current_date] + all_predictions
predictions_df = pd.DataFrame([data_row], columns=column_names)
    
predictions_df.to_csv(output_csv_path, index=False)

# Print the output
print(output)
