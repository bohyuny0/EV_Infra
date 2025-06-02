# 4. Electric Vehicles per 10,000 People
# streamlit run ev10000ppl.py
# 코드는 완벽, 아래 (선택) 하단 안내문 수정!!!! 그리고 주석 한국어 영어로!!!

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.colors
import numpy as np

def get_color_from_scale(value, vmin, vmax, scale_name="Blues"):
    """
    value가 vmin~vmax 사이 어딘가에 있을 때,
    Plotly 내장 색상 스케일(scale_name)에 따라
    대응하는 'rgb(r,g,b)' 형태의 문자열을 반환합니다.
    """
    import re
    if vmax <= vmin:
        return "rgb(0,0,0)"
    ratio = (value - vmin) / (vmax - vmin)
    ratio = max(0, min(1, ratio))
    color_scale = plotly.colors.get_colorscale(scale_name)
    for i in range(len(color_scale) - 1):
        left_ratio, left_color = color_scale[i]
        right_ratio, right_color = color_scale[i+1]
        if left_ratio <= ratio <= right_ratio:
            denom = (right_ratio - left_ratio)
            sub_ratio = 0 if denom == 0 else (ratio - left_ratio) / denom
            def parse_rgb_str(rgb_str):
                m = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str.strip())
                if m:
                    return [int(m.group(1)), int(m.group(2)), int(m.group(3))]
                return [0,0,0]
            lc = parse_rgb_str(left_color)
            rc = parse_rgb_str(right_color)
            c = [int(lc[j] + (rc[j] - lc[j]) * sub_ratio) for j in range(3)]
            return f"rgb({c[0]},{c[1]},{c[2]})"
    return color_scale[-1][1]


# 페이지 설정 (스크립트 최상단에서 한 번만)
st.set_page_config(
    page_title="EV Registration Dashboard",
    page_icon="⚡",
    layout="wide"
)


# 전역 스타일 (Heading h2의 margin-top, margin-bottom을 0으로)
st.markdown("""
<style>
h1, h2 {
    margin-top: 0rem;
    margin-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)



# --- 2. 메인 타이틀 ---
st.title("U.S. Electric Vehicle Registrations in 2023")

# --- 1. 데이터 불러오기 ---
@st.cache_data
def load_map_data():
    data = {
        "state": ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", 
                  "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", 
                  "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts",
                  "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", 
                  "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
                  "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", 
                  "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", 
                  "West Virginia", "Wisconsin", "Wyoming"],
        "state_code": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", 
                       "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", 
                       "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", 
                       "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
        "ev_per_10000": [25, 37, 121, 23, 322, 153, 87, 81, 119, 113, 84, 178, 43, 79, 38, 28, 38, 26, 
                         18, 53, 117, 105, 50, 65, 12, 43, 41, 35, 148, 71, 145, 49, 67, 65, 13, 43, 56, 
                         152, 54, 58, 39, 18, 47, 75, 117, 120, 97, 195, 16, 42, 19],
    }
    df = pd.DataFrame(data)
    return df

@st.cache_data
def load_time_data():
    # CSV 파일에서 (state, year, ev_per_10000) 등이 포함된 데이터를 불러옴
    df = pd.read_csv("ev_per_10000.csv")  
    return df

df_map = load_map_data()
df_time = load_time_data()


max_ev = df_map["ev_per_10000"].max()

# --- (A) 전용 컬러바 figure ---
df_dummy = pd.DataFrame({
    "dummy_x": [0, 1],
    "dummy_y": [0, 1],
    "value":   [0, max_ev]
})
fig_colorbar = px.scatter(
    df_dummy,
    x="dummy_x",
    y="dummy_y",
    color="value",
    color_continuous_scale="Blues",
    range_color=(0, max_ev)
)
# 점, 축, 호버 숨기기 + 컬러바 높이 축소
# 점, 축, 호버 숨기기 + 컬러바 높이 축소
fig_colorbar.update_traces(marker=dict(size=0), hovertemplate=None, hoverinfo="skip")
fig_colorbar.update_xaxes(visible=False)
fig_colorbar.update_yaxes(visible=False)
fig_colorbar.update_layout(
    height=60,  # 컬러바 전체 높이
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(
        orientation="h",
        x=0.54,  # 중앙 정렬
        xanchor="center",
        y=0,
        yanchor="top",
        title=None 
    ),
    title=dict(
        text="<span style='color:gray; font-size:14px; font-weight:normal;'>EV per 10,000 People</span>",  
        x=0.08, 
        y=0.83,
        xanchor="left",
        yanchor="top"
    )
)

# --- (B) 지도(Choropleth) ---
fig_map = px.choropleth(
    df_map,
    color="ev_per_10000",
    custom_data=["state", "ev_per_10000"],
    locationmode="USA-states",
    locations="state_code",
    scope="usa",
    color_continuous_scale="Blues",
    range_color=(0, max_ev),
    labels={"ev_per_10000": "EV per 10,000 People"}
)
fig_map.update_traces(
    hovertemplate="EV per 10,000 People<br>%{customdata[0]}: <b>%{customdata[1]}</b><extra></extra>"
)


# 컬러바 숨김 + 그래프 여백 최소화
fig_map.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    height=380,
    width=600,
    coloraxis_showscale=False
)

# --- (C) 막대그래프 (Top 10) ---
df_top10 = df_map.sort_values("ev_per_10000", ascending=False).head(10)

fig_top10 = px.bar(
    df_top10,
    x="ev_per_10000",
    y="state",
    orientation="h",
    custom_data=["state", "ev_per_10000"],
    color="ev_per_10000",
    color_continuous_scale="Blues",
    range_color=(0, max_ev),
    labels={"ev_per_10000": "EV per 10,000 People", "state": "State"}
)
fig_top10.update_traces(
    hovertemplate="EV per 10,000 People<br>%{customdata[0]}: <b>%{customdata[1]}</b><extra></extra>"
)
fig_top10.update_layout(
    margin=dict(l=0, r=0, t=10, b=0),
    yaxis=dict(autorange="reversed"),
    bargap=0.35,
    height=400,
    coloraxis_showscale=False
)

fig_top10.update_xaxes(
    showgrid=True,          # 그리드선 표시
    gridcolor="lightgray",  # 그리드선 색상
    gridwidth=1,            # 그리드선 두께
    griddash="dot"          # 점선(dotted line) 스타일
)


# --- 3. 레이아웃: 지도 + 막대그래프(좌우), 하단 컬러바 ---
col1, col2 = st.columns([1,1], gap="small")  # 두 컬럼 폭 동일, 간격 작게

with col1:
    st.write("#### EV Density by State per 10,000 People")
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

with col2:
    st.write("#### Top 10 States by EV per 10,000 People")
    st.plotly_chart(fig_top10, use_container_width=True, config={"displayModeBar": False})

# 컬러바를 바로 아래에 표시 (여백 최소화)
st.plotly_chart(fig_colorbar, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# --- 4. Compare 섹션 ---
st.write("## Comparison of EV per 10,000 People")  # 서브타이틀

selected_states = st.multiselect(
    "Select up to 5 states to compare:",
    options=df_map["state"].unique(),
    default=["California", "Washington", "Texas", "Florida", "New York"]
)

if len(selected_states) > 5:
    st.error("Please select up to 5 states only.")
    selected_states = selected_states[:5]

if not selected_states:
    st.warning("Please select at least one state.")
else:
    df_compare = df_map[df_map["state"].isin(selected_states)]
    fig_compare = px.bar(
        df_compare,
        x="state",
        y="ev_per_10000",
        labels={"state": "State", "ev_per_10000": "EV per 10,000 People"},
        color="ev_per_10000",
        color_continuous_scale="Blues",
        range_color=(0, max_ev),
        hover_data=None  # ① 기본 hover_data 끄기
    )
    fig_compare.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
        orientation="v",    # 수직 컬러바
        len=1,            # 그래프 높이의 80%를 차지 (0~1 사이)
        thickness=16,       # 컬러바 두께(px)
        x=1.05,             # 그래프 오른쪽 바깥쪽 (1.0이면 그래프 경계)
        xanchor="left",
        y=0.47,
        yanchor="middle",
        title="EV per 10,000 People"  # 컬러바 제목
        )
    )
    
    fig_compare.update_traces(
    hovertemplate="EV per 10,000 People<br>%{x}: <b>%{y}</b><extra></extra>"
    )


    
    st.plotly_chart(fig_compare, use_container_width=True, config={"displayModeBar": False})

# (선택) 하단 안내문
st.markdown("---")
st.write("""
- **Choropleth**와 **막대그래프**에서 컬러바를 숨기고,
- **하단에 하나의 얇은 컬러바**만 배치해 여백을 최소화했습니다.
""")
