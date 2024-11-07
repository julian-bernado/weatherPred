# Makefile

# ========================================
# Variables
# ========================================

# Directories
MODEL_DIR := model
DATA_DIR := predictions

# Python Script and Output
PREDICT_SCRIPT := $(MODEL_DIR)/test_predictions.py
OUTPUT_FILE := $(DATA_DIR)/test_predictions.csv

# Python Interpreter (modify if needed)
PYTHON := python3

# Docker Variables with Defaults
DOCKER_IMAGE ?= statsbernado/weatherpred
DOCKER_TAG ?= latest
DOCKER_FULL_TAG := $(DOCKER_IMAGE):$(DOCKER_TAG)

# ========================================
# Phony Targets
# ========================================
.PHONY: all predictions clean docker-pull docker-push

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
# Clean Target
# ========================================
clean:
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
