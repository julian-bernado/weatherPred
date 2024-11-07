# Makefile
# Define variables for directories and files
MODEL_DIR := model
DATA_DIR := predictions
PREDICT_SCRIPT := $(MODEL_DIR)/test_predictions.py
OUTPUT_FILE := $(DATA_DIR)/test_predictions.csv

# Default target (optional)
.PHONY: all
all: predictions

# Predictions target
.PHONY: predictions
predictions: $(OUTPUT_FILE)

# Rule to generate the dummy_predict.csv
$(OUTPUT_FILE): $(PREDICT_SCRIPT)
	@echo "Generating $(OUTPUT_FILE) using $(PREDICT_SCRIPT)..."
	python3 $(PREDICT_SCRIPT)

# Clean target to remove the generated file
.PHONY: clean
clean:
	@echo "Removing $(OUTPUT_FILE)..."
	rm -f $(OUTPUT_FILE)
