# WeatherPred

WeatherPred is a reproducible statistical pipeline for forecasting daily temperatures across 20 U.S. cities. For every city, the project predicts the minimum, average, and maximum temperature one through five days ahead.

The project was developed for STATS 604 at the University of Michigan by Julian Bernado, Paolo Borello, Yizhou Gu, Jia Guo, and Sam Rosenberg. The full methodology, results, and post-mortem are available in the [final report](report/report.md).

## Project overview

Each prediction run produces:

- 20 cities
- 5 forecast horizons, from one to five days ahead
- 3 outcomes: minimum, average, and maximum temperature in degrees Fahrenheit
- 300 predictions in total

During the original nine-day evaluation period, from November 26 through December 4, 2024, the pipeline generated 2,700 predictions. Performance was evaluated using mean squared error (MSE). Published weather forecasts and outputs from existing weather-prediction models were not used as features.

## Data and modeling approach

The pipeline combines two public observational data sources:

- [NOAA Global Historical Climatology Network Daily](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily) data for long-term station histories
- [weather.gov](https://www.weather.gov/) observation-history pages for recent conditions not yet available from NOAA

The raw NOAA fixed-width files and weather.gov HTML tables are converted to CSV before feature engineering. The model uses data from 2013 onward and constructs features including:

- Calendar variables such as month, day of year, week of year, and season
- Up to 30 days of lagged temperature and precipitation observations
- Five-day historical averages from the preceding year

The repository implements separate city-level models through a common `MultiStationModel` interface. Three regression methods are compared using time-aware cross-validation:

- Ridge regression
- Random forest regression
- Gaussian process regression

The selected model was ridge regression with a regularization parameter of approximately 615.84. It achieved the lowest cross-validation root mean squared error among the evaluated configurations.

| Model | Selected configuration | CV RMSE |
| --- | --- | ---: |
| Ridge regression | `alpha = 615.84` | 6.67 °F |
| Random forest | `n_estimators = 200`, `min_samples_leaf = 10` | 6.87 °F |
| Gaussian process | Matérn kernel, `length_scale = 10` | 7.28 °F |

## Cities and stations

Predictions are ordered according to the following list.

| City | Station | City | Station |
| --- | --- | --- | --- |
| Anchorage | `PANC` | Boise | `KBOI` |
| Chicago | `KORD` | Denver | `KDEN` |
| Detroit | `KDTW` | Honolulu | `PHNL` |
| Houston | `KIAH` | Miami | `KMIA` |
| Minneapolis | `KMIC`* | Oklahoma City | `KOKC` |
| Nashville | `KBNA` | New York | `KJFK` |
| Phoenix | `KPHX` | Portland, ME | `KPWM` |
| Portland, OR | `KPDX` | Salt Lake City | `KSLC` |
| San Diego | `KSAN` | San Francisco | `KSFO` |
| Seattle | `KSEA` | Washington, DC | `KDCA` |

\* The original project specification listed Minneapolis as `KMSP`; the current implementation uses `KMIC`.

## Quick start with Docker

The published Docker image targets `linux/amd64` and includes the Python environment needed to run the project.

Pull the latest image:

```bash
docker pull statsbernado/weatherpred:latest
```

Open an interactive Bash session inside the container:

```bash
docker run -it --rm statsbernado/weatherpred:latest
```

From the container shell, use the Make targets described below to reproduce the analysis or generate predictions.

### Generate live predictions

```bash
docker run -it --rm statsbernado/weatherpred:latest make predictions
```

The submission format is one CSV-compatible line containing the current date followed by exactly 300 predictions:

```text
"YYYY-MM-DD", XX.X, XX.X, XX.X, ..., XX.X
```

Predictions are ordered by city, then forecast horizon, then outcome. For example:

```text
Anchorage +1 day minimum,
Anchorage +1 day average,
Anchorage +1 day maximum,
Anchorage +2 days minimum,
...,
Washington, DC +5 days maximum
```

The project specification requires no additional standard output when predictions are submitted.

## Local setup

The project uses Python 3.11 in Docker. To run it locally, clone the repository and create an isolated environment:

```bash
git clone https://github.com/julian-bernado/weatherPred.git
cd weatherPred

python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Download and process the data, then perform cross-validation and fit the final model:

```bash
make rawdata
make
```

`make rawdata` downloads the original NOAA and weather.gov observations. The default `make` target converts and processes those files, runs the model search, and saves the selected model as `saved_models/final_model.pkl`.

## Make targets

| Command | Description |
| --- | --- |
| `make` | Convert and process the downloaded data, run cross-validation, and save the selected model. |
| `make rawdata` | Delete and re-download the raw NOAA and weather.gov data. |
| `make convert_data` | Convert NOAA fixed-width files and weather.gov HTML tables to CSV. |
| `make process_data` | Create the model-ready, feature-engineered datasets. |
| `make data` | Download, convert, and process all data. |
| `make cv` | Run the model search if `saved_models/final_model.pkl` is absent or out of date. |
| `make eda` | Regenerate the exploratory-analysis plots. |
| `make predictions` | Download recent observations and produce the current 300-value forecast. |
| `make clean` | Remove generated datasets, models, plots, and intermediate predictions while retaining code and original raw data. |
| `make docker-pull` | Pull `statsbernado/weatherpred:latest`, unless Docker variables are overridden. |
| `make docker-push` | Log in to Docker Hub, build the image, and push it. |

To use a different image or tag with the Docker Make targets:

```bash
make docker-pull DOCKER_IMAGE=<dockerhub-user>/<image-name> DOCKER_TAG=<tag>
```

## Repository structure

| Path | Purpose |
| --- | --- |
| `data/scraper.py` | Download NOAA histories, station metadata, and recent weather.gov observations. |
| `data/converter.py` | Convert downloaded fixed-width and HTML data to CSV. |
| `data/feature_engineering.py` | Build the modeling features and multi-horizon targets. |
| `data/eda.py` | Generate exploratory plots. |
| `models/model.py` | Provide the common multi-station model interface. |
| `models/modules/` | Implement ridge, random forest, and Gaussian process regressors. |
| `models/evaluation/` | Run rolling cross-validation and hyperparameter search. |
| `predictions/download_new.py` | Download and process the observations needed at prediction time. |
| `predictions/predictions.py` | Load the selected model and format the 300 predictions. |
| `report/report.md` | Present the final analysis, results, and lessons learned. |
| `Dockerfile` | Build the Python 3.11 `linux/amd64` execution environment. |
| `makefile` | Define the end-to-end analysis and deployment workflow. |

## Recording predictions

During the original evaluation period, predictions were appended to a CSV file with:

```bash
docker run -it --rm statsbernado/weatherpred:latest make predictions >> predictions.csv
```

Each new row was then committed to GitHub and copied to the course submission sheet before the daily deadline.

## Computational constraints

The original assignment imposed the following limits:

| Task | Limit |
| --- | --- |
| Docker image | Less than 5 GB; `linux/amd64` |
| Full analysis with `make` | Less than 48 hours on 10 CPU cores and 32 GB RAM, without a GPU |
| Live prediction with `make predictions` | Less than 5 minutes on 1 CPU core and 4 GB RAM |

## Known limitations

The final deployed pipeline experienced two data-integration issues documented in the report:

- Newly downloaded weather.gov observations were inadvertently omitted during prediction-time preprocessing, causing many daily forecasts to remain unchanged.
- A weather.gov data failure produced missing predictions on one evaluation day.

These failures emphasize the need for deployment-like integration tests, validation of the newest processed observation, and a fallback policy for unavailable upstream data. See the [discussion in the final report](report/report.md#discussion) for the complete post-mortem.

## Reproducibility

The workflow is organized around Make targets, caches intermediate outputs, and packages its dependencies in Docker. Raw downloads are kept separate from converted and feature-engineered data so each stage can be rerun independently.
