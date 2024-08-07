import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

def fetch_om_data(latitude, longitude, freq):
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"

    value_param =  ["temperature_2m", "relative_humidity_2m", "rain", "direct_radiation"]
   
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": value_param,
        "start_date": "2020-06-16",
        "end_date": "2024-06-30",
        "timezone": "America/Chicago"
    }

    try:
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.

        data = response.Hourly()


        data_temperature_2m = data.Variables(0).ValuesAsNumpy()
        data_relative_humidity_2m = data.Variables(1).ValuesAsNumpy()
        data_rain = data.Variables(2).ValuesAsNumpy()
        data_direct_radiation = data.Variables(3).ValuesAsNumpy()

        data = {"date": pd.date_range(
            start = pd.to_datetime(data.Time(), unit = "s", utc = True),
            end = pd.to_datetime(data.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = data.Interval()),
            inclusive = "left"
        )}

        data["temperature_2m"] = data_temperature_2m
        data["relative_humidity_2m"] = data_relative_humidity_2m
        data["rain"] = data_rain
        data["direct_radiation"] = data_direct_radiation

        dataframe = pd.DataFrame(data = data)

        if freq == "daily":
            # Take the average of the 24 hours to get daily averages
            daily_dataframe = dataframe.resample('D', on='date').mean().reset_index()
            return daily_dataframe
        elif freq == "monthly":
            # First, resample to daily averages
            daily_dataframe = dataframe.resample('D', on='date').mean().reset_index()
            # Then, resample the daily averages to get monthly averages
            monthly_dataframe = daily_dataframe.resample('M', on='date').mean().reset_index()
            return monthly_dataframe
        else:
            return dataframe
    
    except Exception as e:
        print(f"Failed to fetch data from OpenMeteo: {e}")
        return e


