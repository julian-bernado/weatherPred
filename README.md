# Our Schedule
## To-Do (all by next meeting)
- Docker image set up
- Set up some structure to scrape weather data from WeatherUnderground
- Set up custom commands for Docker image

## Next Meeting
- Meet on Wednesday, November 5th 3:30pm - 5pm

# Docker
Here's a pretty comprehensive explanation of how the Docker stuff works here. First, to use docker you need to start the docker engine, so download Docker Desktop and launch it before using any of the docker commands. So that people don't have to interface with docker that much, I just have commands in the makefile that will do what you need. 
* `make docker-pull` will pull the current docker image. You want to do this before running any predictions in docker, but if you're just modifying code in the GitHub, you don't need to do this.
* `make docker-push` will login to docker, build the image based on the current state of the repo, and push it to our dockerhub. You should run this whenever you make a significant modification to the GitHub so that our docker image is up to date. It's not super necessary for every little change, but definitely do this after you're done modifying the repo in one sitting.
In addition, I have the make predictions command working right now with temporary files that you can use to see the functionality right now, but once that code is less temporary, you should change the Makefile targets or let me know and I can tend to the Makefiles.

Happy Dockering -Julian

# Project Overview
* Predict the minimum, average, and maximum daily temperature (in Fahrenheit) at each of 20 cities
* Predictions should be made 1, 2, 3, 4, and 5 days ahead, every day from Tuesday, November 26 to Wednesday, December 4 (inclusive).
* Predictions are due at noon.
* Your first predictions are due at noon on Nov 26, and will be for Nov 27 -- Dec 1
* Your final predictions are due at noon on Dec 4 and will be for Dec 5 -- Dec 9
* You will make a total of 2,700 predictions: (3 variables) x (20 cities) x (5 days) x (9 days) = 2,700
* Goal is to minimize mean squared error

## The cities
* Anchorage       PANC
* Boise           KBOI
* Chicago         KORD
* Denver          KDEN
* Detroit         KDTW
* Honolulu        PHNL
* Houston         KIAH
* Miami           KMIA
* Minneapolis     KMSP
* Oklahoma City   KOKC
* Nashville       KBNA
* New York        KJFK
* Phoenix         KPHX
* Portland ME     KPWM
* Portland OR     KPDX
* Salt Lake City  KSLC
* San Diego       KSAN
* San Francisco   KSFO
* Seattle         KSEA
* Washington DC   KDCA

## Project timeline
* Monday, Nov 25: Model finalized, code committed to Github, Docker image uploaded to Dockerhub
* Tuesday, Nov 26: Begin making daily predictions, due at noon daily
* Tuesday, Dec 3: Presentations
* Wednesday, Dec 4: Final day making predictions; report due

## Data and analysis
* Any publicly available data you want
* Any methods you want

Except:
	•	Weather predictions
	•	Weather prediction models

## Reproducibility
* Write report in markdown
* Compose all analyses in a notebook environment
* Track changes using git
* Collaborate via a github repo
* Organize code into a coherent workflow
* Use makefiles
* Cache intermediate outputs
* Save entire analysis in docker image
* Docker image can also be run to make live predictions

## Docker image
* Docker image should be uploaded to Dockerhub, and shared with me and the GSI
* Should include:
* Raw data (exactly as downloaded from the internet)
* All code, including to:
* Download raw data
* Fit models
* Download current weather conditions and make predictions
* Intermediate outputs, e.g.,
* Cleaned/processed data
* Fitted models
* Should support linux/amd64 platform

### Running the Docker image
* The command docker run -it --rm yourdockerhubname/yourimagename should provide a bash terminal where commands can be run to reproduce the analysis (see next slide)
* The command docker run -it --rm yourdockerhubname/yourimagename make predictions should output that day's predictions to the screen, and then quit

### Running the Docker image (default terminal)
* The command docker run -it --rm yourdockerhubname/yourimagename should provide a bash terminal where commands can be run to reproduce the analysis
* The following commands should be available:
* make clean -- deletes everything except for the code (i.e., markdown files) and raw data (as originally downloaded)
* make -- runs all analyses (except downloading raw data and making current predictions)
* make predictions -- makes current predictions and outputs them to the screen
* make rawdata -- deletes and re-downloads the raw data
* Other make commands, if/as appropriate

### Running the Docker image (predictions)
* The command docker run -it --rm yourdockerhubname/yourimagename make predictions should output that day's predictions to the screen, and then quit
* The output should look like: "YYYY-MM-DD", XX.X, XX.X, XX.X, ..., XX.X where
* "YYYY-MM-DD" is the current date
* There are 300 numbers of the form XX.X where each X is a digit
* The numbers are predictions in degrees fahrenheit
* The order is given by: Anchorage +1 day, minimum; Anchorage +1 day, average; Anchorage +1 day, maximum; Anchorage +2 days, minimum; ...; Washington DC +5 days, maximum
* No other output should be displayed

### Recording your predictions
Every day before noon you should:
* Run docker run -it --rm yourdockerhubname/yourimagename make predictions >> predictions.csv
* Commit the updated predictions.csv to github
* Add your new predictions to the class's Google Sheets document (OK if completed a little after noon)

### Computational resources
* Your docker image should be no larger than 5GB
* make should run in under 48 hours, assuming
* 10 cores
* 32GB RAM
* No GPU
* make predictions should run in under 5 minutes, assuming
* 1 core
* 4GB RAM
* MWireless connection
