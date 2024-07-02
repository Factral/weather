import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

def fetch_om_data(latitude, longitude, freq):
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"


    value_param = "temperature_2m" if freq == "hourly" else "temperature_2m_mean"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        freq: value_param,
        "start_date": "2020-06-16",
        "end_date": "2024-06-30",
        "timezone": "America/Chicago"
    }

    try:
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        if freq == "daily":
            hourly = response.Daily()
        elif freq == "hourly":
            hourly = response.Hourly()



        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m

        hourly_dataframe = pd.DataFrame(data = hourly_data)

        return hourly_dataframe
    
    except Exception as e:
        print(f"Failed to fetch data from OpenMeteo: {e}")
        return e


