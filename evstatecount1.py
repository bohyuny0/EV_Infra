# 3-1. evstatecount1
# streamlit run evstatecount1.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit 페이지 설정
st.set_page_config(
    page_title="U.S. Electric Vehicle Registrations",
    page_icon="⚡",
    layout="wide"
)

st.title("U.S. Electric Vehicle Registrations in 2023")

# EV 등록 데이터
state_ev_data = {
    'California': 1256646, 'Texas': 230125, 'Florida': 254878, 'New York': 131250,
    'Illinois': 99573, 'Ohio': 50393, 'Georgia': 92368, 'North Carolina': 70164,
    'Michigan': 50284, 'Pennsylvania': 70154, 'Washington': 152101, 'Arizona': 89798,
    'Colorado': 90083, 'Massachusetts': 73768, 'Virginia': 84936, 'New Jersey': 134753,
    'Tennessee': 33221, 'Indiana': 26101, 'Minnesota': 37050, 'Maryland': 72139,
    'Missouri': 26861, 'Wisconsin': 24943, 'Oregon': 64361, 'Nevada': 47361, 'South Carolina': 20873,
    'Kentucky': 11617, 'Alabama': 13047, 'Louisiana': 8150, 'Utah': 39998, 'Iowa': 9031,
    'Kansas': 11271, 'Oklahoma': 22843, 'Arkansas': 7108, 'Mississippi': 3590, 'Nebraska': 6920,
    'New Mexico': 10276, 'West Virginia': 2758, 'Hawaii': 25565, 'Idaho': 8501, 'Maine': 7377,
    'New Hampshire': 9861, 'Montana': 4608, 'Rhode Island': 6396, 'Delaware': 8435, 'South Dakota': 1675,
    'North Dakota': 959, 'Alaska': 2697, 'Vermont': 7816, 'Connecticut': 31557, 'District of Columbia': 8066, 'Wyoming': 1139
}

df = pd.DataFrame(list(state_ev_data.items()), columns=['State', 'EV_Count'])

# 주 이름을 주 약어로 매핑
state_codes = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}
df['State_Code'] = df['State'].map(state_codes)

max_ev = df["EV_Count"].max()

# --- (A) 컬러바 (범례) 설정 ---
df_dummy = pd.DataFrame({"dummy_x": [0, 1], "dummy_y": [0, 1], "value": [0, max_ev]})
fig_colorbar = px.scatter(
    df_dummy, x="dummy_x", y="dummy_y", color="value", color_continuous_scale="Blues", range_color=(0, max_ev)
)
fig_colorbar.update_traces(marker=dict(size=0), hoverinfo="skip")
fig_colorbar.update_layout(
    height=60,
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(
        orientation="h",
        x=0.54, xanchor="center",
        y=0, yanchor="top",
        title=None
    ),
    title=dict(
        text="<span style='color:gray; font-size:14px; font-weight:normal;'>Electric Vehicles</span>",
        x=0.08, y=0.83,
        xanchor="left", yanchor="top"
    )
)

# --- (B) 미국 지도 (Choropleth Map) ---
fig_map = px.choropleth(
    df,
    locations="State_Code",
    locationmode="USA-states",
    color="EV_Count",
    custom_data=["State", "EV_Count"],
    scope="usa",
    color_continuous_scale="Blues",
    range_color=(0, max_ev),
    labels={"EV_Count": "Electric Vehicles"}
)
fig_map.update_traces(
    hovertemplate="Electric Vehicles<br>%{customdata[0]}: <b>%{customdata[1]:,}</b><extra></extra>"
)
fig_map.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    height=380, width=600,
    coloraxis_showscale=False
)

# --- (C) 상위 10개 주 (막대그래프) ---
df_top10 = df.sort_values("EV_Count", ascending=False).head(10)
fig_top10 = px.bar(
    df_top10,
    x="EV_Count", y="State",
    orientation="h",
    custom_data=["State", "EV_Count"],
    color="EV_Count",
    color_continuous_scale="Blues",
    range_color=(0, max_ev),
    labels={"EV_Count": "Electric Vehicles", "State": "State"}
)
fig_top10.update_traces(
    hovertemplate="Electric Vehicles<br>%{customdata[0]}: <b>%{customdata[1]:,}</b><extra></extra>"
)
fig_top10.update_layout(
    margin=dict(l=0, r=0, t=10, b=0),
    yaxis=dict(autorange="reversed"),
    bargap=0.35,
    height=400,
    coloraxis_showscale=False
)

fig_top10.update_xaxes(
    showgrid=True, gridcolor="lightgray", gridwidth=1, griddash="dot"
)

# --- (3) 지도 + 막대그래프 (2열 레이아웃) ---
col1, col2 = st.columns([1, 1], gap="small")

with col1:
    st.write("#### EV Registrations by State (2023)")
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

with col2:
    st.write("#### 🏆 Top 10 States by EV Registrations")
    st.plotly_chart(fig_top10, use_container_width=True, config={"displayModeBar": False})

# 컬러바를 하단에 배치
st.plotly_chart(fig_colorbar, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# Add a dropdown menu to filter by state
st.subheader("🔍 Search for a State's EV Registration")

# df["State"].unique()를 sorted()로 감싸서 알파벳순으로 정렬
state_list = sorted(df["State"].unique())

selected_state = st.selectbox("Select a state:", state_list)

filtered_data = df[df["State"] == selected_state]
st.write(f"**{selected_state}** has **{filtered_data['EV_Count'].values[0]:,}** registered electric vehicles.")

