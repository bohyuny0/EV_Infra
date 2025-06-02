# 1. evlocation
# streamlit run evlocation.py
# 한국어 주석 영어로 고치기!!!!

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
# import warnings
# warnings.filterwarnings('ignore')

# 페이지 레이아웃 wide 모드
st.set_page_config(
    layout="wide",
    page_icon="⚡"
)

# CSV 불러오기
df = pd.read_csv('EV_Station_Location.csv')

# 지도 생성
map_usa = folium.Map(location=[39.5, -98.35], zoom_start=4)
marker_cluster = MarkerCluster().add_to(map_usa)

# MarkerCluster에 충전소 위치 추가
for idx, row in df.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=row.get('Station_Name'),
        icon=folium.Icon(color='green', icon='bolt', prefix='fa')
    ).add_to(marker_cluster)

# Streamlit 앱에 지도 표시
st.title("Locations of Electric Vehicle Charging Stations in the U.S.")
# width를 최대한 확장하고 높이를 원하는 만큼 조정
st_folium(map_usa, width=1800, height=900)

