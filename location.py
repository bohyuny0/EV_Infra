# # streamlit run location.py

# import streamlit as st
# import pandas as pd
# import folium
# from folium.plugins import MarkerCluster
# from streamlit_folium import st_folium

# # 데이터 로드 (캐싱 적용)
# @st.cache_data
# def load_ev_data():
#     return pd.read_parquet('EV_Station_Location.parquet')

# # Folium 지도 생성 (캐싱 적용)
# @st.cache_resource
# def create_ev_map(data):
#     # 지도 생성
#     m = folium.Map(location=[39.5, -98.35], zoom_start=4)
#     marker_cluster = MarkerCluster().add_to(m)

#     # 모든 데이터 포인트 표시 (샘플링 없음)
#     for idx, row in data.iterrows():
#         folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=row.get('Station_Name', 'Unknown'),
#             icon=folium.Icon(color='green', icon='bolt', prefix='fa')
#         ).add_to(marker_cluster)

#     return m

# st.title("Locations of Electric Vehicle Charging Stations in the U.S.")

# # 데이터 로드
# df = load_ev_data()

# # 지도 생성 및 렌더링
# map_usa = create_ev_map(df)
# st_folium(map_usa, width=1000, height=600)

# st.title("EV Registration Dashboard")
# st.markdown("### Overview: Electric Vehicle Data and Infrastructure in the U.S.")

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(
    page_title="EV Registration Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 제목
st.title("Locations of Electric Vehicle Charging Stations in the U.S.")

# 데이터 로드 (빠르게 캐싱)
@st.cache_data
def load_ev_data():
    return pd.read_parquet('EV_Station_Location.parquet')

# 지도 생성 함수 (HTML로 변환하여 저장)
def create_ev_map_html(data):
    # Folium 지도 생성
    m = folium.Map(location=[39.5, -98.35], zoom_start=4.5, tiles="CartoDB positron")
    
    # 위치 데이터만 리스트로 변환 (속도 개선)
    locations = list(zip(data['Latitude'], data['Longitude']))
    
    # FastMarkerCluster 적용
    MarkerCluster(locations).add_to(m)
    
    # Folium 지도 객체를 HTML로 변환하여 반환
    return m._repr_html_()

# 데이터 로드
df = load_ev_data()

# 데이터 샘플링 (1000개만 랜덤 선택)
df_sample = df.sample(n=1000, random_state=42)

# 지도 HTML을 세션 상태에 저장하여 리렌더링 방지
if "ev_map_html" not in st.session_state:
    st.session_state.ev_map_html = create_ev_map_html(df_sample)

# HTML을 Streamlit에 직접 삽입 (깜빡임 방지)
components.html(st.session_state.ev_map_html, height=900, width=1290)
