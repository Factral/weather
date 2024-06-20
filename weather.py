import folium as fl
from streamlit_folium import st_folium
import streamlit as st

st.set_page_config(page_title="Weather Project")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: grey;'>Weather project</h1>", unsafe_allow_html=True)

def get_pos(lat,lng):
    return lat,lng

m = fl.Map()

m.add_child(fl.LatLngPopup())

st.text("Click on the map to select a point and get the weather data.")
map = st_folium(m, height=350, width=700)

data = None
if map.get('last_clicked'):
    print(map['last_clicked'])
    data = get_pos(map['last_clicked']['lat'] , map['last_clicked']['lng'])

if data is not None:
    print(data)

source_data = st.radio('Select the source of the data', options=['Api', 'Dane', 'Local (subir archivo)'], 
          horizontal=True, index=None)


st.divider()
if data is not None and source_data is not None:
    st.write("here will be the graph of the weather data based on the selected point and the source of the data")
    st.write(data)
    st.write(f"you selected the source: {source_data}")
