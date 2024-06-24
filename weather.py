import folium as fl
from streamlit_folium import st_folium
import streamlit as st
import requests
import pandas as pd
from sodapy import Socrata
import plotly.express as px

def fetch_om_data(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "relative_humidity_2m", "rain", "shortwave_radiation"]
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        data = response.json()
        
        if 'hourly' not in data:
            st.error("Hourly data key not found in the response.")
            return pd.DataFrame()  # Return an empty DataFrame if 'hourly' data is not available
        
        hourly_data = data['hourly']
        time_series = pd.to_datetime(hourly_data['time'], infer_datetime_format=True)
        df = pd.DataFrame(hourly_data, index=time_series)
        return df
    
    except requests.RequestException as e:
        st.error(f"HTTP Request failed: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

    return pd.DataFrame()

def plot_time_series(dataframe, title):
    if not dataframe.empty:
        fig = px.line(dataframe, x=dataframe.index, y=['temperature_2m', 'relative_humidity_2m', 'rain', 'shortwave_radiation'],
                      labels={'value': 'Measurement', 'variable': 'Variables'},
                      title=title)
        return fig
    else:
        st.error("No data to plot.")
        
def main():
    
    hide_default_format = """
           <style>
           #MainMenu {visibility: hidden; }
           footer {visibility: hidden;}
           </style>
           """
           
    st.markdown(hide_default_format, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #fae6e6;'>Weather project</h1>", unsafe_allow_html=True)
    
    m = fl.Map()
    m.add_child(fl.LatLngPopup())
    map_widget = st_folium(m, height=500, width=1000)
    
    source_data = st.radio('Select the source of the data', ['OpenMeteo', 'Dane', 'Local (upload file)'], horizontal=True)
    
    if map_widget.get('last_clicked'):
        lat, lng = map_widget['last_clicked']['lat'], map_widget['last_clicked']['lng']
        if source_data == "OpenMeteo":
            weather_data = fetch_om_data(lat, lng)
            if not weather_data.empty:
                fig = plot_time_series(weather_data, "Hourly Weather Data")
                if fig:
                    st.plotly_chart(fig)
                else:
                    st.error("Failed to plot data.")
            else:
                st.error("No data returned from OpenMeteo.")
                
        elif source_data == "Dane":
            dane_data = fetch_dane_data("Dane")
            st.write(dane_data)
    
    st.divider()
    st.write("Add more interactive elements as required")

if __name__ == "__main__":
    main()
