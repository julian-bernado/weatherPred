# Makefile

# ========================================
# Variables
# ========================================

# Directories
MODEL_DIR := models
SAVED_MODELS_DIR := saved_models
PREDICTIONS_DIR := predictions
DATA_DIR := data
IMAGE_DIR := images

# Python Interpreter (modify if needed)
PYTHON := python3

# Docker Variables with Defaults
DOCKER_IMAGE ?= statsbernado/weatherpred
DOCKER_TAG ?= latest
DOCKER_FULL_TAG := $(DOCKER_IMAGE):$(DOCKER_TAG)

# ========================================
# Phony Targets
# ========================================
.PHONY: all predictions clean cv docker-pull docker-push rawdata convert_data process_data

# ========================================
# Default Target
# ========================================
all: convert_data process_data cv

# ========================================
# Predictions Target
# ========================================
predictions:
	@rm -f predictions/new_data/*.html
	@rm -f predictions/new_data/processed/*.csv
	@rm -f predictions/new_data/to_csv/*.csv
	@$(PYTHON) -m predictions.download_new
	@$(PYTHON) -m predictions.predictions

# ========================================
# Cross Validation Target
# ========================================
cv: $(SAVED_MODELS_DIR)/final_model.pkl

$(SAVED_MODELS_DIR)/final_model.pkl: $(MODEL_DIR)/evaluation/grid_search.py
	$(PYTHON) -m $(MODEL_DIR).evaluation.grid_search

# ========================================
# Raw Data Target: deletes rawdata if it exists and runs scraper.py
# ========================================
rawdata:
	@echo "Removing raw data..."
	rm -rf $(DATA_DIR)/raw_data
	@echo "Running scraper.py..."
	$(PYTHON) $(DATA_DIR)/scraper.py

# ========================================
# convert_data Target: runs data conversion scripts (noaa_converter.py)
# ========================================
convert_data:
	@echo "Removing converted data..."
	rm -rf $(DATA_DIR)/raw_data/noaa/to_csv
	rm -rf $(DATA_DIR)/raw_data/weather_gov/to_csv
	@echo "Running converter.py..."
	$(PYTHON) $(DATA_DIR)/converter.py

data: rawdata convert_data process_data

# ========================================
# EDA Target: runs EDA script (eda.py)
# ========================================
eda:
	@echo "Removing EDA plots..."
	rm -rf $(IMAGE_DIR)/plots
	@echo "Running eda.py..."
	$(PYTHON) $(DATA_DIR)/eda.py

# ========================================
# process_data Target: runs data processing scripts (feature_engineering.py)
# ========================================
process_data:
	@echo "Removing processed data..."
	rm -rf $(DATA_DIR)/processed_data
	@echo "Running feature_engineering.py..."
	$(PYTHON) $(DATA_DIR)/feature_engineering.py

# ========================================
# Clean Target
# ========================================
clean:
	@echo "Removing processed data..."
	rm -rf $(DATA_DIR)/processed_data
	@echo "Removing EDA plots..."
	rm -rf $(IMAGE_DIR)/plots
	@echo "Removing $(OUTPUT_FILE)..."
	rm -f $(OUTPUT_FILE)
	@echo "Removing cross validation CSVs"
	rm -f models/evaluation/evaluation_results/random_forest_hyperparameters.csv
	rm -f models/evaluation/evaluation_results/ridge_hyperparameters.csv
	rm -f models/evalutions/evaluation_results/gp_hyperparameters.csv
	@echo "Removing saved models"
	rm -f saved_models/final_model.pkl
	@echo "Removing intermediate predictions"
	rm -f predictions/intermediate/*.csv
	@echo "Removing newest data"
	rm -f predictions/new_data/*.html
	rm -f predictions/new_data/to_csv/*.csv
	rm -f predictions/new_data/processed/*.csv

# ========================================
# Docker Pull Target
# ========================================
docker-pull:
	@echo "Pulling Docker image $(DOCKER_FULL_TAG)..."
	docker pull $(DOCKER_FULL_TAG)
	@echo "Successfully pulled $(DOCKER_FULL_TAG)."

# ========================================
# Docker Push Target
# ========================================
docker-push:
	@echo "Starting Docker push operations..."
	@echo "Logging into Docker..."
	docker login
	@echo "Building Docker image $(DOCKER_FULL_TAG)..."
	docker build -t $(DOCKER_FULL_TAG) .
	@echo "Pushing Docker image $(DOCKER_FULL_TAG)..."
	docker push $(DOCKER_FULL_TAG)
	@echo "Docker push operations completed successfully."
