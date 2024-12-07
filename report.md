# STATS 604: Project 4 Report

## Julian Bernado, Paolo Borello, Yizhou Gu, Jia Guo, Sam Rosenberg

# Introduction
The goal of this project is to use statistical techniques to train and evaluate the performance of models used to predict weather in major cities across the United States. A list of 20 cities of interest was selected, forming a representative sample of diverse climates and regions across the country. For each city, the goal is to make weather predictions over more than a week. For each day and each city, we aim to predict the daily minimum, maximum, and average temperatures for one to five days out.

While physics-based models are commonly used for weather prediction, statistical approaches offer numerous benefits as a replacement or supplement to these models. Statistical models are typically more computationally efficient at time of prediction, readily allow for the incorporation of historical data, allow for the incorporation of uncertainty quantification, and can provide additional interpretability.

# Data

We collected data from two sources: the National Oceanic and Atmospheric Administration ([NOAA](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all)) and [weather.gov](https://forecast.weather.gov/data/obhistory/). 

We chose these datasets because they offer reliable, granular, and historical weather information across a wide range of locations in the United States, which is essential for building accurate predictive models. NOAA provides comprehensive daily weather datasets in `.dly` format, a robust foundation of standardized and high-quality observations aggregated from multiple (30+) sources. These datasets are frequently updated, with past week’s observations refined multiple times to ensure better accuracy. However, NOAA data often excludes the most recent two days of weather records, making it necessary to supplement it with data from weather.gov, which offers near real-time, detailed weather observations. This combination of historical depth and up-to-date information made these sources ideal for our project.

To retrieve the data, we developed custom web scraping scripts for each source. For NOAA, we designed a scraper to download `.dly` files, which are fixed-width format (FWF) files containing daily weather observations. For weather.gov, our scraper fetched the relevant HTML pages containing observational data for various weather stations.

After collecting the raw data, we implemented a secondary custom script to convert both the `.dly` files and the scraped HTML data into standardized `.csv` files. This conversion involved parsing the FWF structure of the `.dly` files and extracting relevant fields, as well as cleaning and formatting the HTML data into a tabular format. These `.csv` files formed the basis of our exploratory data analysis and modeling pipeline.

### Details About the Raw Data

The `.dly` files from NOAA follow a structured, fixed-width format, where each row corresponds to a specific weather station and contains daily observations of multiple weather variables. These include temperature (maximum, minimum, and average), precipitation, snowfall, snow depth, and other meteorological measurements. Each file contains metadata such as the station ID, latitude, longitude, and elevation, providing geographic context for the observations.

The data from weather.gov, on the other hand, is presented as HTML pages, where observational data is updated regularly and includes parameters like temperature, wind speed, humidity, pressure, and visibility. Unlike NOAA’s fixed-width files, the HTML format required extensive preprocessing to extract relevant fields and align them with the NOAA dataset.

Both datasets required meticulous cleaning and validation to handle missing values, inconsistencies in station identifiers, and differences in temporal resolution.

# EDA

# Models

After gathering and processing our data, we effectively had 20 separate datasets, one for each city. This presented a key modeling choice:

1. **Train a single model** on the combined dataset, leveraging inter-city relationships.  
2. **Train separate models** for each city, focusing on local weather characteristics.  

While combining datasets may benefit highly expressive models by learning latent inter-city dependencies, the diverse weather patterns across cities (e.g., San Francisco's maritime climate vs. New York City's continental climate) led us to favor city-specific models. Initially, we considered using a **Graph Neural Network (GNN)** to automatically learn latent weather factors and propagate this information across neighboring cities. However, due to time and computational constraints, we opted for simpler, more interpretable models.

## Multi-Station Model Framework

To manage city-specific models efficiently, we developed a `MultiStationModel` class that treats each city’s model as a submodule stored in a dictionary. Each submodule adheres to a unified interface with the following methods:

1. **`fit`**: Train the model on city-specific data.  
2. **`predict`**: Generate predictions for new data.  
3. **`evaluate`**: Assess model performance using standard metrics.  
4. **`get_params`**: Retrieve hyperparameters for tuning or inspection.  
5. **`set_params`**: Update hyperparameters as needed.

This modular framework allows for streamlined training, prediction, and evaluation across all cities, while supporting easy integration of new models. Batch operations across cities (e.g., training all models with a single function call) further enhance pipeline efficiency. Additionally, this design aligns well with cross-validation procedures, enabling systematic assessment of model performance.

## Models Implemented

We implemented three regression models within this framework:

1. **Ridge Regression**  
   Ridge regression applies $\ell_2$ regularization to a linear model, controlling overfitting by penalizing large coefficients. This model is particularly well-suited to datasets where linear relationships dominate, offering both simplicity and computational efficiency.  

2. **Random Forest Regression (RFR)**  
   Random forests combine predictions from multiple decision trees to model complex, nonlinear relationships. This ensemble approach is robust to overfitting and works well with high-dimensional data, though at the cost of reduced interpretability compared to linear models.

3. **Gaussian Process Regression (GPR)**  
   GPR is a probabilistic model that provides both predictions and confidence intervals. It is particularly powerful for capturing non-linear patterns, albeit with high computational costs, making it suitable for smaller datasets.

The parameters to cross-validate for each model are as follows:

| **Model**                | **Parameter**        | **Description**                                      |
|--------------------------|----------------------|------------------------------------------------------|
| **Ridge Regression**     | `alpha`              | Regularization strength to control overfitting       |
| **Random Forest**        | `n_estimators`       | Number of trees in the forest                        |
|                          | `min_samples_leaf`   | Minimum number of samples required to be a leaf node |
| **Gaussian Process**     | `kernel`             | Kernel function for covariance                       |
|                          | `length_scale`       | Characteristic length scale of the kernel            |


# Cross-Validation

Given the temporal nature of our data, a simple train-test-split approach was not appropriate. As such, we performed a rolling-window cross-validation approach. In more detail, we would train our model with a given hyperparameter configuration on all days up to some day $d$, then we would predict the five days following $d$. We did this for the final 14 days $d$ in our dataset such that we could evaluate our predictions five days out. As such, the size of our sliding window is 5, we slide by 1-day, and we have 14 different folds of cross-validation. Mean squared error across these 14 folds was averaged and reported for each configuration of hyperparamters across the three model. After running cross-validation, our code automatically selects the model and hyperparameter configuration resulting the lowest MSE. Note that since we only have one-layer of cross-validation, we have that our test-set error is lower than what is expected in the actual evaluation. However, since we did not need to estimate our prediction error, we did not nest our cross validation. Cross-validation was conducted sequentially across all cities. While we could have chosen different models or hyperparameter configurations for different cities, for simplicity of the code-base and performance of daily predictions, from cross-validation we extract a single model. It is worthwhile to distinguish though, in-line with the data description above, each mode is only trained on one city.

Hyperparameters were tested using a grid approach: for each model we established a range of values for each hyperparameter, then tested each possible combination of hyperparameter values. The grid used for training hyperparameters is displayed below. Initially the grid of hyperparameter choices was denser, but extensive modulation of this grid was done in order to guarantee that training would be completed in 48 hours; training and fitting each model in 20 stations across 14 varying datasets incurred a large computational cost.


We found that ridge regression with a penalty parameter of 615.84 achieved the lowest Root-Mean Squared Error: 

# Discussion

In this section, we will discuss the key implementation issues that came as part of this project as well as overall difficulties and future directions for predicting weather data.

## Implementation Issues

A series of related issues led to our model outputting the same prediction for most days and NA values for December 1st. In the face of these issues, we conducted a post-mortem to understand wwhat went wrong. At their core, these issues stem from inconsistent behavior of the two sources from which we scrape our data as well as insufficient time given on our part to test the pipeline. While we were disappointed to see this behavior of our model at the time of the code freeze, we learned some key lessons regarding the deployment of code that provides dynamic real-time outputs. I will first give an account of what led to these undesirable outputs and then talk through the lessons that we have learned as a group in the face of such a failure.  

Due to the five minute limit placed on the daily execution, we implemented time checks for most operations in our code base. When first establishing the pipeline, we found that code executed well under this limit. Furthermore, we found that scraping data from both NOAA and weather.gov worked consistently. However, two issues arose only a couple days before the code-freeze deadline. First, we found that the time to download NOAA data was highly variable which decreased our certainty that we would be under the five minute limit. Second, we found that sometimes reading the NOAA data resulted in a 404 page not found error. As such, quick changes needed to be made to the pipeline. We resolved to only download weather.gov data upon each call of `make predictions`. However, the proximity of this discovery to the deadline led to this new patchwork code containing an error that correctly downloaded weather.gov data, but dropped the relevant rows before making a prediction. So for all days of making a prediction, our code was predicting five days out from the final day of training data. As such, our predictions remained constant throughout the prediction window.

A first lesson, thematically shared between testing code and testing models with cross-validation, is that code should be tested in an environment most similar to the actual deployment environment. If we hope for predictions to work in the period of code-freeze, it would have been advantageous to set an earlier deadline and enact a code-freeze on ourselves. If we were to freeze code and test long enough before the deadline, we would have had ample time to observe both the issues with downloading NOAA data as well as the error in our code causing predictions to be identical across days. 

A second lesson is that we should plan for "worst" case scenarios when certain factors are outside of our control. Initially to keep track of computational time, we would check how long a script would take to run once that script had been finalized. After confirming that a part of the script ran in adequate time, we moved on to the next part. However, instead of treating the computation as a relatively constant value, we should have planned for contingencies from the beginning. In terms of computational time, this would have made us develop our `weather.gov` code early enough to spot the relevant issue. In addition, on December 1st our model outputted NA values due to an issue with `weather.gov` on that day. Were we to plan most robustly for this sort of failure, we could have hard-coded values to output at that time to save us from a row of NAs.

As Statisticians, we are often more concerned with the theoretical or methodological questions concerned with our work. However, this experience serves as a humbling reminder that no amount of measure theory can save us from coding errors.

## Final Remarks