# 3. evstatecount 
# streamlit run evstatecount.py
# 거의 완료:
# Top 10 States with the Most EV Registrations -- 테이블 열 너비 조절 가능하지 해보기
# 아래 막대바 Electric Vehicles 왼쪽으로 텍스트 가능한지

import streamlit as st
import plotly.express as px
import pandas as pd

# Streamlit title
st.set_page_config(
    page_title="U.S. Public EV Charging Infrastructure",
    page_icon="⚡",
    layout="wide"
)

st.title("U.S. Electric Vehicle Registrations by State (2023)")

# EV registration data by state
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

# Mapping state names to abbreviations
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


# Plotly choropleth map
fig = px.choropleth(
    df,
    locations='State_Code',
    locationmode="USA-states",
    color='EV_Count',
    hover_name='State',
    hover_data={'EV_Count': False},  # Hide default EV_Count in the hover box
    color_continuous_scale="Blues",
    range_color=(0, df['EV_Count'].max()),
    labels={'EV_Count': 'Electric Vehicles'}
)

# ✅ Custom hover template (Only EV Count is bold)
fig.update_traces(
    hovertemplate="Electric Vehicles<br>%{hovertext}: <b>%{z:,}</b><extra></extra>"
)

# Customize the map layout
fig.update_layout(
    geo=dict(
        scope='usa',
        projection_scale=1,
        showland=True,
        landcolor="rgb(229, 229, 229)",
        showcoastlines=True,
        coastlinecolor="white",
        showlakes=False,
        lakecolor="white",
        countrycolor="white",
        subunitcolor="white",
        domain={'y': [0, 1]}
    ),
    dragmode=False,
    # title_text="Electric Vehicles Registered in 2023",
    # title_x=0.35,
    coloraxis_colorbar=dict(
        orientation='h',
        thickness=16,
        len=0.9,
        x=0.5,
        xanchor='center',
        y=-0.05,  # 🔹 범례 위치를 살짝 올림
        yanchor='top',
        title=dict(
            text="Electric Vehicles",  # ✅ 텍스트 유지
            side="top"  # ✅ 텍스트를 막대 위쪽에 정렬 (standoff 제거)
        )
    )
)


# 상단 제목을 동일한 크기로 조정하고 col1의 중앙에 배치
st.markdown(
    """
    <style>
    .custom-title {
        font-size: 22px !important;
        font-weight: bold;
        text-align: center;
        margin-bottom: -20px;
    }
    .custom-subtitle {
        font-size: 22px !important;
        font-weight: bold;
        text-align: left;
        margin-left: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Create two columns: Left for the map, Right for the table (adjust width for balance)
col1, col2 = st.columns([1.8, 1.2])  

# Left Column: U.S. EV Registration Map
with col1:
    st.markdown('<div class="custom-title">Electric Vehicles Registered in 2023</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

# Right Column: Top 10 States Table
with col2:
    st.markdown('<div class="custom-subtitle">Top 10 States with the Most EV Registrations</div>', unsafe_allow_html=True)
    # st.markdown("##### Top 10 States with the Most EV Registrations")

    # Sort by EV count and add Rank column (starting from 1)
    top_10_states = df.sort_values(by="EV_Count", ascending=False).head(10).reset_index(drop=True)
    top_10_states.insert(0, "Rank", range(1, len(top_10_states) + 1))

    # ✅ Apply CSS for better column width control
    st.markdown(
        """
        <style>
        div[data-testid="stDataFrame"] table {
            width: 100% !important;
        }
        div[data-testid="stDataFrame"] th {
            text-align: center !important;
            font-weight: bold !important;
            padding: 10px !important;
        }
        div[data-testid="stDataFrame"] td {
            text-align: center !important;
            padding: 8px !important;
        }
        div[data-testid="stDataFrame"] th:nth-child(1), 
        div[data-testid="stDataFrame"] td:nth-child(1) {
            width: 15% !important;  /* Rank column smaller */
        }
        div[data-testid="stDataFrame"] th:nth-child(2), 
        div[data-testid="stDataFrame"] td:nth-child(2),
        div[data-testid="stDataFrame"] th:nth-child(3), 
        div[data-testid="stDataFrame"] td:nth-child(3) {
            width: 42.5% !important;  /* State and EV_Count evenly sized */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ✅ Display table with controlled column widths
    st.dataframe(
        top_10_states[["Rank", "State", "EV_Count"]],
        hide_index=True,  # Remove extra index column
        use_container_width=True  # Keep container width adjustment
    )

st.markdown("---")

# Add a dropdown menu to filter by state
st.subheader("🔍 Search for a State's EV Registration")

# df["State"].unique()를 sorted()로 감싸서 알파벳순으로 정렬
state_list = sorted(df["State"].unique())

selected_state = st.selectbox("Select a state:", state_list)

filtered_data = df[df["State"] == selected_state]
st.write(f"**{selected_state}** has **{filtered_data['EV_Count'].values[0]:,}** registered electric vehicles.")
