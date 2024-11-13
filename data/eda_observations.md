# EDA Observations

## Missingness
* For all cities, limited missingness (<10%) for PRCP, TMAX, TMIN
* Much more missingness for TAVG (~65-75%)
  * Generally, missingness for TAVG seems to occur prior to 2013, then decrease to none
    * KDCA has some major missingness from 2023 onward (~66% / year)
    * KMIC has 100% missingness from 2006 onward

## Climate time series
### Daily time series
* PRCP
  * Plots are too noisy to see trends
* TAVG
  * Clear seasonality, need to average across year or month to see better
* TMAX, TMIN
  * Some seasonality also, but less obvious than TAVG

### Monthly time series
* PRCP
  * Clear monthly patterns, but very different patterns by city
* TXXX
  * Clear monthly patterns with same general shape, but month of peak varies by city

### Yearly time series
* PRCP
  * No clear trend
* TAVG
  * Missingness makes it tough to discern trend
* TMAX
  * Average within year increasing, but pattern varies by city
* TMIN
  * Average within year very obviously increasing, but pattern varies by city

## Cross-correlation
* Ignore TAVG for now because of missingness
* Drop NAs in other columns
* Round to 2 decimal places
* Precipitation not very predictive of either temperature variable
  * Degree of correlation depends on city
  * Higher correlations for KBOI and PNHL; KPDX, KSAN, KSEA, and KSFO (latter group very strong, relative to others)
* Lags of TMIN/TMAX most correlated with themselves
  * Also correlated with lags of one another though
  * Degree of correlation varies by city
  * Up to 30 days out, most cross-correlations still >50%