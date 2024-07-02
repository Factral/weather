import folium as fl
from streamlit_folium import st_folium
import streamlit as st
import plotly.express as px
from openmeteo import fetch_om_data


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
map_widget = st_folium(m, width=900)


st.divider()

source_data = st.radio('Select the source of the data', ['OpenMeteo', 'Dane', 'Local (upload file)'], horizontal=True)

# Initialize session state
if 'last_clicked' not in st.session_state:
    st.session_state['last_clicked'] = None
if 'freq' not in st.session_state:
    st.session_state['freq'] = 'daily'
if 'variable' not in st.session_state:
    st.session_state['variable'] = 'temperature_2m'

# Update session state with map click
if map_widget.get('last_clicked'):
    st.session_state['last_clicked'] = map_widget['last_clicked']
    lat, lng = map_widget['last_clicked']['lat'], map_widget['last_clicked']['lng']

    # Normalize the lat and lng  180E and 180W
    if lng < -180:
        lng = 360 + lng

    st.session_state['lat'] = lat
    st.session_state['lng'] = lng

# another radio to slect the variable, one of ["temperature_2m", "relative_humidity_2m", "rain", "direct_radiation"]
st.session_state['variable'] = st.radio('Select the variable', ["temperature_2m", "relative_humidity_2m", "rain", "direct_radiation"], index=["temperature_2m", "relative_humidity_2m", "rain", "direct_radiation"].index(st.session_state['variable']), horizontal=True)

# Update session state with frequency selection
st.session_state['freq'] = st.radio('Select the frequency of the data', ['hourly', 'daily', 'monthly'], index=['hourly', 'daily', 'monthly'].index(st.session_state['freq']), horizontal=True)


if st.session_state['last_clicked'] and source_data == "OpenMeteo":
    lat = st.session_state['lat']
    lng = st.session_state['lng']
    freq = st.session_state['freq']
    
    weather_data = fetch_om_data(lat, lng, freq)

    print(weather_data)


    fig = px.line(weather_data, x='date', y=st.session_state['variable'], title='Temperature over Time', labels={'dates': 'Time', 'temperature_2m': 'Temperature (°C)'})
    st.plotly_chart(fig)

st.divider()
