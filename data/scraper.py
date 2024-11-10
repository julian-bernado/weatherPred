# National Oceanic and Atmospheric Administration (NOAA) data scraper

# Importing libraries
import os
import requests

# Base path for the NOAA data (get folder in which this file is located)
out_noaa_path = os.path.join(os.path.dirname(__file__), 'raw_data', 'noaa')
# Base URL for the NOAA data
base_noaa_url = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all'

# Dictionary mapping city names to airport codes
city_to_airport = {
    "Anchorage": "PANC",
    "Boise": "KBOI",
    "Chicago": "KORD",
    "Denver": "KDEN",
    "Detroit": "KDTW",
    "Honolulu": "PHNL",
    "Houston": "KIAH",
    "Miami": "KMIA",
    "Minneapolis": "KMIC",
    "Oklahoma City": "KOKC",
    "Nashville": "KBNA",
    "New York": "KJFK",
    "Phoenix": "KPHX",
    "Portland ME": "KPWM",
    "Portland OR": "KPDX",
    "Salt Lake City": "KSLC",
    "San Diego": "KSAN",
    "San Francisco": "KSFO",
    "Seattle": "KSEA",
    "Washington": "KDCA",
}
# Dictionary mapping airport codes to NOAA station IDs
airport_to_noaa = {
    "PANC": "USW00026451",
    "KBOI": "USW00024131",
    "KORD": "USW00094846",
    "KDEN": "USW00003017",
    "KDTW": "USW00094847",
    "PHNL": "USW00022521",
    "KIAH": "USW00012960",
    "KMIA": "USW00012839",
    "KMIC": "USW00094960",
    "KOKC": "USW00013967",
    "KBNA": "USW00013897",
    "KJFK": "USW00094789",
    "KPHX": "USW00023183",
    "KPWM": "USW00014764",
    "KPDX": "USW00024229",
    "KSLC": "USW00024127",
    "KSAN": "USW00023188",
    "KSFO": "USW00023234",
    "KSEA": "USW00024233",
    "KDCA": "USW00013743",
}

if __name__ == '__main__':
    # Create the output directory if it doesn't exist
    if not os.path.exists(out_noaa_path):
        os.makedirs(out_noaa_path)
    # Loop over the city names and airport codes
    for city, airport in city_to_airport.items():
        print(f"Downloading data for {city}")
        url = f"{base_noaa_url}/{airport_to_noaa[airport]}.dly"
        # Download the data
        response = requests.get(url)
        # Save the data to a file
        with open(f"{out_noaa_path}/{airport}.dly", 'wb') as f:
            f.write(response.content)
    print("Downloaded all data")