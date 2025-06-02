# 2. publicevinfra
# streamlit run publicevinfra.py
# 완료
# 추가로 데이터 소스만 하기

import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 전체 화면 설정
st.set_page_config(
    page_title="U.S. Public EV Charging Infrastructure",
    page_icon="⚡",
    layout="wide"
)

# 2. 제목
st.title("U.S. Public EV Charging Infrastructure Over Time")

# 3. CSV 파일 불러오기
file_path = "U.S. Public Electric Vehicle Charging Infrastructure.csv"
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()

# 4. 숫자형 변환 (콤마 제거 → 숫자로)
df["EV Charging Ports"] = df["EV Charging Ports"].astype(str).str.replace(",", "")
df["Station Locations"] = df["Station Locations"].astype(str).str.replace(",", "")

df["EV Charging Ports"] = pd.to_numeric(df["EV Charging Ports"], errors="coerce")
df["Station Locations"] = pd.to_numeric(df["Station Locations"], errors="coerce")
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

# 5. 결측치 제거 및 연도 순 정렬
df = df.dropna(subset=["Year", "EV Charging Ports", "Station Locations"])
df = df.sort_values("Year")

df["Year"] = df["Year"].astype(int)


# 6. 연도 슬라이더
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())
start_year, end_year = st.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(2013, 2023),
    step=1
)

# 7. 연도 범위로 데이터 필터링
filtered_df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

# 8. Plotly에서 2개 컬럼을 라인 차트로 그리고 싶으면 "melt" 형태로 변환 (Wide → Long)
melted_df = filtered_df.melt(
    id_vars="Year",
    value_vars=["Station Locations", "EV Charging Ports"],
    var_name="Category",      # Station Locations / EV Charging Ports
    value_name="Count"
)

# 9. Plotly 라인 차트 생성
fig = px.line(
    melted_df,
    x="Year",
    y="Count",
    color="Category",         # 라인 구분
    markers=True,             # 각 지점에 마커 표시
    title=f"U.S. Public EV Charging Infrastructure ({start_year}-{end_year})"
)

# y축에 콤마 포맷 적용: Plotly는 기본적으로 툴팁이나 축에 천단위 구분 적용을 자동 지원하지만
# 더 구체적으로 format 지정도 가능
fig.update_layout(
    yaxis=dict(tickformat=",")  # 천단위 콤마
)

# 10. Streamlit에 Plotly 차트 표시 (이미지가 아닌 인터랙티브 차트)
st.plotly_chart(fig, use_container_width=True)
