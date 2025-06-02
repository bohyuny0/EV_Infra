# U.S. All Grades All Formulations Retail Gasoline Prices
# Data source: U.S. Energy Information Administration

# streamlit run gasolineprices.py

# 2007	2.843
# 2008	3.299
# 2009	2.406
# 2010	2.835
# 2011	3.576
# 2012	3.68
# 2013	3.575
# 2014	3.437
# 2015	2.52
# 2016	2.25
# 2017	2.528
# 2018	2.813
# 2019	2.691
# 2020	2.258
# 2021	3.1
# 2022	4.059
# 2023	3.635
# 2024	3.424

import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 전체 화면 설정
st.set_page_config(
    page_title="U.S. Public EV Charging Infrastructure",
    page_icon="⚡",
    layout="wide"
)

# 1. 제목 설정
st.title("U.S. All Grades All Formulations Retail Gasoline Prices")

# 2. 데이터 정의 (연도별 휘발유 가격)
gas_prices = {
    2007: 2.843, 2008: 3.299, 2009: 2.406, 2010: 2.835, 2011: 3.576,
    2012: 3.68, 2013: 3.575, 2014: 3.437, 2015: 2.52, 2016: 2.25,
    2017: 2.528, 2018: 2.813, 2019: 2.691, 2020: 2.258, 2021: 3.1,
    2022: 4.059, 2023: 3.635
}

# 3. 데이터프레임 변환 (연도를 int로 변환)
df_gas_prices = pd.DataFrame(list(gas_prices.items()), columns=["Year", "Gasoline Price"])
df_gas_prices["Year"] = df_gas_prices["Year"].astype(int)  # 정수형 변환

# 4. 연도 슬라이더 추가
start_year, end_year = st.slider(
    "Select Year Range",
    min_value=min(gas_prices.keys()),
    max_value=max(gas_prices.keys()),
    value=(2010, 2023),
    step=1
)

# 5. 선택한 연도 범위의 데이터 필터링
filtered_df = df_gas_prices[(df_gas_prices["Year"] >= start_year) & (df_gas_prices["Year"] <= end_year)]

# 6. Plotly 라인 차트 생성
fig = px.line(
    filtered_df,
    x="Year",
    y="Gasoline Price",
    markers=True,
    title=f"U.S. Retail Gasoline Prices ({start_year}-{end_year})"
)

# 🔹 X축을 범주형으로 변환하여 연도 소수점 문제 해결
fig.update_layout(
    xaxis=dict(type="category"),  # 연도를 카테고리로 설정하여 정확한 값 표시
    yaxis=dict(tickformat=".3f")  # 소수점 3자리까지 표시
)

# 7. Streamlit에 Plotly 차트 표시
st.plotly_chart(fig, use_container_width=True)

