# Makefile

# ========================================
# Variables
# ========================================

# Directories
MODEL_DIR := models
PREDICTIONS_DIR := predictions
DATA_DIR := data
IMAGE_DIR := images

# Python Script and Output
PREDICT_SCRIPT := $(MODEL_DIR)/test_predictions.py
OUTPUT_FILE := $(PREDICTIONS_DIR)/test_predictions.csv

# Python Interpreter (modify if needed)
PYTHON := python3

# Docker Variables with Defaults
DOCKER_IMAGE ?= statsbernado/weatherpred
DOCKER_TAG ?= latest
DOCKER_FULL_TAG := $(DOCKER_IMAGE):$(DOCKER_TAG)

# ========================================
# Phony Targets
# ========================================
.PHONY: all predictions clean docker-pull docker-push raw_data convert_data

# ========================================
# Default Target
# ========================================
all: predictions

# ========================================
# Predictions Target
# ========================================
predictions: $(OUTPUT_FILE)

# Rule to generate the dummy_predict.csv
$(OUTPUT_FILE): $(PREDICT_SCRIPT)
	@$(PYTHON) $(PREDICT_SCRIPT)
	@cat $(OUTPUT_FILE)

# ========================================
# Raw Data Target: deletes raw_data if it exists and runs scraper.py
# ========================================
raw_data:
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
	@echo "Running noaa_converter.py..."
	$(PYTHON) $(DATA_DIR)/noaa_converter.py

data: raw_data convert_data

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
	@echo "Removing raw and processed data..."
	rm -rf $(DATA_DIR)/raw_data
	rm -rf $(DATA_DIR)/processed_data
	@echo "Removing EDA plots..."
	rm -rf $(IMAGE_DIR)/plots
	@echo "Removing $(OUTPUT_FILE)..."
	rm -f $(OUTPUT_FILE)

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
