# streamlit run final.py

import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import numpy as np


# Page setting (Default expand sidebar)
st.set_page_config(
    page_title="EV Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("☰ Dashboard Menu")
st.sidebar.write("Navigate through different sections.")

# Add menu option
menu_option = st.sidebar.radio("Select a section:", ["Overview", "EV Charging Stations", "EV Infrastructure & Gas Price Trends", "EV Statistics I", "EV Statistics II", "Conclusion"])

# Fill the remaining space of the sidebar and add developer information
with st.sidebar:
    st.markdown("<div style='height: 300px;'></div>", unsafe_allow_html=True)  # Add adjustable empty space
    st.markdown("<p style='position: absolute; bottom: -90px; font-size: 14px; color: gray;'>" "Developed by <b>Grace Yang</b></p>", unsafe_allow_html=True)

# Display on screen
st.title("Electric Vehicle Dashboard")
st.write(f"**Selected Menu:** {menu_option}")

if menu_option == "Overview":
    st.write("#### Impact of EV Charging Infrastructure on EV Adoption & Accessibility Across the U.S.")
    st.markdown("""
        <div style="padding-bottom: 4px;">
            The project <b>"Impact of EV Charging Infrastructure on EV Adoption & Accessibility Across the U.S."</b> 
            visualizes key data collected at the end of 2023. The dashboard provides interactive maps to clearly illustrate 
            the distribution and accessibility of public EV charging stations nationwide, highlighting how this infrastructure influences electric vehicle adoption. 
            Additionally, it enables analysis of relationships between charging station availability, population distribution, 
            EV adoption trends, and the potential impact of gasoline price volatility on infrastructure expansion and EV uptake.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.write("#### 📌 Research Questions: What are we going to explore?")
    st.markdown("""
    <ol>
        <li>EV Charging Station Distribution</li>
        <li>EV Charging Station Infrastructure Growth & Gasoline Prices</li>
        <li>EV Charging Station Density vs. EV Adoptions</li>
        <li>EV Charging Station Density vs. Population Density</li>
    </ol>
    """, unsafe_allow_html=True)


elif menu_option == "EV Charging Stations":
    st.header("📍 Locations of EV Charging Stations")
    st.write("This map visualizes **1,000 randomly sampled** EV charging station locations across the United States, including Alaska, Hawaii, and Washington D.C. The stations are selected from a larger dataset to provide a representative overview. Use the zoom function to get a detailed view of specific states or cities!")
    #############################
    # 1. EV Charging Stations Map
    #############################
    
    # Load data quickly with caching
    @st.cache_data
    def load_ev_data():
        return pd.read_parquet('EV_Station_Location.parquet')

    # Load data
    df = load_ev_data()
    df_sample = df.sample(n=1000, random_state=42) # Data sampling (Randomly select only 1000)

    # Map generation function
    def create_ev_map(data):
        m = folium.Map(location=[39.5, -98.35], zoom_start=4.4, tiles="CartoDB positron", control_scale=True)
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=row.get("Station Name", "EV Station"),
                icon=folium.Icon(color="green", icon="bolt", prefix="fa")
            ).add_to(marker_cluster)

        return m

    # Map generation and display
    ev_map = create_ev_map(df_sample)
    st_folium(ev_map, width="100%", height=650)  # Auto adjust ratio

    # Data source & Abbreviations
    st.markdown("")
    st.markdown("")
    st.markdown("""
        <div style="font-size: 14px; color: gray; margin-bottom: -100px; padding: 0px;">
            <b>Acronyms and Abbreviations</b>: EV = Electric Vehicle  
            <br>
            <b>Source</b>: Electric Vehicle Registrations by State from the Alternative Fuels Data Center (AFDC)
        </div>
    """, unsafe_allow_html=True)

    
    
elif menu_option == "EV Infrastructure & Gas Price Trends":
    #####################################################
    # 2. U.S. Public EV Charging Infrastructure Over Time
    #####################################################
    st.header("U.S. Public EV Charging Infrastructure Over Time")
    st.write("This graph shows the growth of public EV charging infrastructure in the U.S. from 2007 to 2023, highlighting the increase in both station locations and charging ports.")

    # Remove slider background (Apply CSS)
    st.markdown("""
        <style>
            /* Remove entire slider background */
            div[data-testid="stSlider"] > div {
                background: transparent !important;
            }
            /* Adjust slider bar inner style */
            div[data-baseweb="slider"] {
                background: transparent !important;
                border: none !important;
            }
            /* Adjust slider handle style */
            div[data-testid="stThumbValue"] {
                background: transparent !important;
                color: #FF4B4B !important;  /* Slider number color */
            }
            /* Selected range bar (Progress bar) */
            div[data-testid="stRangeSliderBar"] {
                background: red !important;  /* Changeable to desired color */
            }
        </style>
    """, unsafe_allow_html=True)

    # Load CSV file
    file_path = "U.S. Public Electric Vehicle Charging Infrastructure.csv"
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    # Convert to number (Remove commas → Numeric)
    df["EV Charging Ports"] = df["EV Charging Ports"].astype(str).str.replace(",", "")
    df["Station Locations"] = df["Station Locations"].astype(str).str.replace(",", "")

    df["EV Charging Ports"] = pd.to_numeric(df["EV Charging Ports"], errors="coerce")
    df["Station Locations"] = pd.to_numeric(df["Station Locations"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Remove missing values and sort by year
    df = df.dropna(subset=["Year", "EV Charging Ports", "Station Locations"])
    df = df.sort_values("Year")
    
    # Convert Year to integer (Fix decimal issue)
    df["Year"] = df["Year"].astype(int)

    # # Year slider
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())
    start_year, end_year = st.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(2013, 2023),
        step=1
    )

    # Filter data by year range
    filtered_df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

    # Convert to "melt" format for Plotly line chart (Wide → Long)
    melted_df = filtered_df.melt(
        id_vars="Year",
        value_vars=["EV Charging Ports", "Station Locations"],
        var_name="Category",
        value_name="Count"
    )

    # Create Plotly line chart
    fig = px.line(
        melted_df,
        x="Year",
        y="Count",
        color="Category",                # Line separation
        markers=True,                    # Show markers at each point
        title=f"U.S. Public EV Charging Infrastructure ({start_year}-{end_year})",
        color_discrete_map={
        "EV Charging Ports": "#8fc134",  # Green
        "Station Locations": "#f1bf46"   # Yellow
        }
    )

    # Modify legend items (Set inside update_layout)
    fig.for_each_trace(lambda t: t.update(customdata=[[t.name]] * len(t.x)))
    
    # Adjust line thickness and point size
    fig.update_traces(
        hoverlabel=dict(namelength=0),
        line=dict(width=3), 
        marker=dict(size=6),
        hovertemplate="%{customdata[0]}<br>"
                    "Year: <b>%{x}</b><br>"
                    "Count: <b>%{y:,}</b>"
    )

    # Apply comma format to y-axis
    fig.update_layout(
        xaxis=dict(
            type="category",    # Set x-axis as categorical to display only integer years
            tickmode="linear",  # Force display of all years (Prevent omissions)
            tickvals=filtered_df["Year"].unique(),  # Set x-axis tick values (Year)
        ),
        yaxis=dict(tickformat=",")  # Thousand separator comma
    )

    # Display Plotly chart in Streamlit (Interactive, not an image)
    st.plotly_chart(fig, use_container_width=True)
    
    # Graph description
    st.markdown("""
    <b>Key Insights: U.S. Public EV Charging Infrastructure (2007-2023)<b>
    <ul>
        <li><b>Rapid Growth Since 2011:</b> The expansion of EV charging infrastructure began to accelerate around 2011, with a steady increase in both station locations and charging ports.</li>
        <li><b>Faster Growth in Charging Ports:</b>The number of EV Charging Ports has grown at a significantly higher rate than Station Locations, suggesting an increase in multi-port charging stations.</li>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")
    st.markdown("")
    
    # Data source
    st.markdown("""
    <div style="font-size: 14px; color: gray;">
        <b>Source</b>: U.S. Public Electric Vehicle Charging Infrastructure from Alternative Fuels Data Center (AFDC)
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown("---")
    
    # Title: U.S. All Grades All Formulations Retail Gasoline Prices
    st.header("U.S. All Grades All Formulations Retail Gasoline Prices")
    st.write("""
             This graph shows the annual average retail gasoline prices in the U.S. from 2007 to 2023, measured in dollars per gallon. Use the slider below to adjust the year range and explore trends over time.
            """)
    
    # Data definition (Gasoline price by year)
    gas_prices = {
        2007: 2.843, 2008: 3.299, 2009: 2.406, 2010: 2.835, 2011: 3.576,
        2012: 3.68, 2013: 3.575, 2014: 3.437, 2015: 2.52, 2016: 2.25,
        2017: 2.528, 2018: 2.813, 2019: 2.691, 2020: 2.258, 2021: 3.10,
        2022: 4.059, 2023: 3.635
    }

    # Convert DataFrame (Change year to int)
    df_gas_prices = pd.DataFrame(list(gas_prices.items()), columns=["Year", "Dollars per Gallon"])
    df_gas_prices["Year"] = df_gas_prices["Year"].astype(int)

    # Add year slider
    start_year, end_year = st.slider(
        "Select Year Range",
        min_value=min(gas_prices.keys()),
        max_value=max(gas_prices.keys()),
        value=(max(2013, min(gas_prices.keys())), 2023),  # Default value (If 2013 or later)
        step=1,
        key="year_range_slider"
    )
     
    # Add "Category" column and convert to long format
    df_gas_prices["Category"] = ""
    melted_df = df_gas_prices.melt(id_vars=["Year"], value_vars=["Dollars per Gallon"], var_name="Category", value_name="Count" )

    # Filter data by selected year range
    filtered_df = df_gas_prices[(df_gas_prices["Year"] >= start_year) & (df_gas_prices["Year"] <= end_year)]
   
    # Create Plotly line chart
    fig = px.line(
        filtered_df,
        x="Year",
        y="Dollars per Gallon",
        color="Category",
        markers=True,
        title=f"U.S. Retail Gasoline Prices ({start_year}-{end_year})",
        color_discrete_map={"Dollars per Gallon": "#467cd1"}    # Line color
    )
    fig = px.line(
        filtered_df,
        x="Year",
        y="Dollars per Gallon",
        color="Category",  
        markers=True,
        title=f"U.S. Retail Gasoline Prices ({start_year}-{end_year})",
        color_discrete_map={"Dollars per Gallon": "#467cd1"}
    )

    # Convert x-axis to categorical to fix year decimal issue
    fig.update_layout(
        xaxis=dict(type="category"),    # Set year as category to display exact values
        yaxis=dict(tickformat="$.2f"),  # Display up to 3 decimal places
        legend=dict(                    # Set legend
            title="Category",           # Legend title
            x=1.025,                    # Position outside to the right on x-axis
            y=1                         # Align top on y-axis
        )
    )
    
    # Modify legend items (Set inside update_layout)
    fig.for_each_trace(lambda t: t.update(name="U.S. Gas Prices"))

    # Apply line and marker styles to legend & Add legend names
    fig.update_traces(
        hoverlabel=dict(namelength=0),
        line=dict(width=3, color="#467cd1"),
        marker=dict(size=6, color="#467cd1", symbol="circle"),
        hovertemplate="U.S. Gas Prices<br>"
                    "Year: <b>%{x}</b><br>"
                    "Dollars per Gallon: <b>$%{y:.2f}</b>",
        showlegend=True
    ) 
    
    # Display Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)    
    
    # Insights
    st.markdown("""
    <b>Key Insights: U.S. Retail Gasoline Prices (2007-2023)<b>
    <ul>
        <li><b>2009 Drop:</b> Prices fell sharply due to the global financial crisis.</li>
        <li><b>2014 Peak & 2016 Drop:</b> Prices peaked around <b>$3.50/gal</b> before dropping below <b>$2.50/gal</b>, influenced by oil supply increases.</li>
        <li><b>2020 Low & 2022 Surge:</b> Prices hit a low in 2020 due to the COVID-19 pandemic, then surged past <b>$4.00/gal</b> in 2022 due to supply chain issues & global energy shocks.</li>
        <li><b>2023 Decline:</b> Prices slightly decreased after the 2022 spike, reflecting market stabilization.</li>
        <li>This trend highlights <b>economic downturns</b>, <b>oil supply shifts</b>, and <b>global disruptions</b> as key drivers of gasoline price fluctuations.</li>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")
    st.markdown("")
    
    # Data source & Abbreviations
    st.markdown("""
    <div style="font-size: 14px; color: gray; margin-bottom: -100px; padding: 0px;">
        <b>Acronyms and Abbreviations</b>: EV = Electric Vehicle  
        <br>
        <b>Source</b>: U.S. Energy Information Administration
    </div>
    """, unsafe_allow_html=True)
    
    
elif menu_option == "EV Statistics I":
    #########################################################
    # 3. U.S. EV Registrations by State (2023) & State Filter
    #########################################################
    st.header("U.S. Electric Vehicles Registrations by State")
    
    # EV registration data (dictionary-based)
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
    df_state = pd.DataFrame(list(state_ev_data.items()), columns=['State', 'EV_Count'])

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
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'District of Columbia': 'DC', 'Wyoming': 'WY'
    }
    df_state['State_Code'] = df_state['State'].map(state_codes)

    max_ev = df_state["EV_Count"].max()

    # Dedicated colorbar figure
    df_dummy = pd.DataFrame({
        "dummy_x": [0, 1], 
        "dummy_y": [0, 1], 
        "value": [0, max_ev]
    })
    fig_colorbar = px.scatter(
        df_dummy, 
        x="dummy_x", 
        y="dummy_y", 
        color="value", 
        color_continuous_scale="Blues", 
        range_color=(0, max_ev)
    )

    fig_colorbar.update_traces(marker=dict(size=0), hovertemplate=None, hoverinfo="skip")
    fig_colorbar.update_xaxes(visible=False)
    fig_colorbar.update_yaxes(visible=False)
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

    # US Map (Choropleth Map)
    fig_map = px.choropleth(
        df_state,
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
    
    # Top 10 States (Bar Chart)
    df_top10 = df_state.sort_values("EV_Count", ascending=False).head(10)
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

    # Map + Bar Chart (Two-Column Layout)
    col1, col2 = st.columns([1, 1], gap="small")

    with col1:
        st.write("#### 🚙 EV Registrations by State (2023)")
        st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})   # Add Zoom In/Out and Modebar

    with col2:
        st.write("#### Top 10 States by EV Registrations")
        st.plotly_chart(fig_top10, use_container_width=True, config={"displayModeBar": False})

    # Position colorbar at the bottom
    st.plotly_chart(fig_colorbar, use_container_width=True, config={"displayModeBar": False})

    st.markdown("")
    st.markdown("")

    # Data source
    st.markdown("""
    <div style="font-size: 14px; color: gray;">
        <b>Source</b>: TransAtlas from the Alternative Fuels Data Center (AFDC)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Add a dropdown menu to filter by state
    st.write("#### 🔍 Search for a State's EV Registration")

    # Sort alphabetically using sorted()
    state_list = sorted(df_state["State"].unique())
    selected_state = st.selectbox("Select a state:", state_list)
    
    filtered_data = df_state[df_state["State"] == selected_state]
    st.write(f"**{selected_state}** has **{filtered_data['EV_Count'].values[0]:,}** registered electric vehicles.")

    st.markdown("---")
    
    # Load data (Charging station data + EV registration data)
    @st.cache_data
    def load_ev_data():
        return pd.read_csv("EV_Station_Location.csv")  # Charging Station Data

    @st.cache_data
    def load_ev_registration_data():
        return pd.read_csv("Population Estimate & EV Count.csv")  # EV Registration Data
    
    @st.cache_data
    def load_ev_density_data():
        return pd.read_csv("ev_per_10000.csv")  # Population Density Data

    df_stations = load_ev_data()
    df_ev = load_ev_registration_data()
    
    # Use existing 'state_codes' dictionary (Convert state code → Full name)
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
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'District of Columbia': 'DC', 'Wyoming': 'WY'
    }

    # Convert state code → Full name
    state_full_names = {v: k for k, v in state_codes.items()}
    
    # Calculate number of EV charging stations by state
    df_stations_count = df_stations.groupby("State").size().reset_index(name="Charging_Stations")

    # Clean column names in EV registration data
    df_ev = df_ev.rename(columns={"EV registration by state": "EV_Registrations", "2023": "Population"})

    # Exclude US total data and keep only state-level data
    df_ev = df_ev[df_ev["State"] != "US"]

    # Merge data (Based on State)
    df_merged = pd.merge(df_stations_count, df_ev, on="State", how="inner")
    
    # Calculate charging station density per 10K people
    df_merged["Charging Stations per 10k"] = df_merged["Charging_Stations"] / (df_merged["Population"] / 10000)
    df_merged["State_Full"] = df_merged["State"].map(state_full_names)  # Add state full name

    # Remove missing values (Exclude states with no population or charging station data)
    df_merged = df_merged.dropna(subset=["Charging Stations per 10k", "EV_Registrations"])

    # Calculate correlation coefficient
    correlation = df_merged["Charging Stations per 10k"].corr(df_merged["EV_Registrations"])

    # Title
    st.header("Relationship Between EV Charging Station Density & EV Adoptions")
    
    # Add explanation of EV charging station density calculation method
    st.markdown("""
    To calculate the **charging station density** for each state, the total number of charging stations is divided by the state’s population normalized per 10,000 residents. 
    This provides a standardized measure of charging station availability relative to population size.
    """)

    # Convert EV_Registrations to integer
    df_merged["EV_Registrations"] = df_merged["EV_Registrations"].astype(float).round(0).astype(int)


    # Scatter plot with linear regression
    fig = px.scatter(
        df_merged,
        x="Charging Stations per 10k",
        y="EV_Registrations",
        title="EV Charging Station Density vs. EV Adoptions",
        labels={"Charging Stations per 10k": "Charging Stations per 10K People", "EV_Registrations": "EV Adoptions"},
        trendline="ols"    # Add linear regression line
    )
    
    fig.update_traces(marker=dict(size=8, opacity=0.7, color="#4C72B0"))

    # Display graph
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    st.markdown("""
    <b>Key Insights: EV Charging Station Density vs. EV Adoptions</b>
    <ul>
        <li>This graph illustrates the relationship between EV charging station density per 10,000 people and EV adoptions by state in the U.S.</li>
        <li>An <b>Ordinary Least Squares (OLS) regression line</b> is included, with the following equation:</li>
    </ul>
    <div style="text-align: center; font-size: 16px; font-weight: bold; margin-top: -0.2cm; margin-bottom: 5px;">
        EV Adoptions = 46,721.5 × Charging Stations per 10K − 11,071.2</div>
    <ul>
        <li><b>R² value (0.083349)</b> is <b>low</b>, indicating a weak correlation between charging station density and EV adoptions.</li>
        <li>The majority of the data points are concentrated in the lower charging station density range (1-2 per 10K people), with some states showing high EV adoptions.</li>
        <li>A higher charging station density does not necessarily lead to higher EV adoption, as other factors such as policies, infrastructure, and economic conditions may also play a role.</li>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    df_stations = load_ev_data()
    df_ev = load_ev_registration_data()
    df_density = load_ev_density_data()

    # Create a dictionary to convert state names to state codes
    us_state_abbreviations = {
        "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
        "colorado": "CO", "connecticut": "CT", "delaware": "DE", "district of columbia": "DC",
        "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID", "illinois": "IL",
        "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
        "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
        "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
        "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
        "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
        "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
        "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
        "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY"
    }
    
    # Convert state names to codes in the EV density data
    df_density["State"] = df_density["state"].str.strip().str.lower().map(us_state_abbreviations)

    # Select population density data
    df_latest_density = df_density[df_density["year"] == df_density["year"].max()]

    # Calculate the number of EV charging stations by state
    df_stations_count = df_stations.groupby("State").size().reset_index(name="Charging_Stations")

    # Clean column names in the EV registration data
    df_ev = df_ev.rename(columns={"EV registration by state": "EV_Adoptions", "2023": "Population"})
    df_ev = df_ev[df_ev["State"] != "US"]

    # Standardize the 'State' column (Convert to uppercase)
    df_stations_count["State"] = df_stations_count["State"].str.strip().str.upper()
    df_ev["State"] = df_ev["State"].str.strip().str.upper()
    df_latest_density["State"] = df_latest_density["State"].str.strip().str.upper()

    # Merge data based on the 'State' column
    df_merged = pd.merge(df_stations_count, df_ev, on="State", how="inner")
    df_merged = pd.merge(df_merged, df_latest_density[["State", "ev_per_10000"]], on="State", how="inner")

    # Calculate charging station density per 100K people
    df_merged["Charging Stations per 10k (log)"] = df_merged["Charging_Stations"] / (df_merged["Population"] / 10000)

    # Remove missing values
    df_merged = df_merged.dropna(subset=["Charging Stations per 10k (log)", "ev_per_10000"])
    
    # Apply log transformation
    df_merged["Charging Stations per 10k (log)"] = np.log1p(df_merged["Charging Stations per 10k (log)"])
    df_merged["EV Adoptions (log)"] = np.log1p(df_merged["EV_Adoptions"])
    df_merged["log_ev_per_10000"] = np.log1p(df_merged["ev_per_10000"])
    
    # Research Question 1: EV Charging Station Density vs EV Adoption Rate
    st.header("EV Charging Station Density vs. EV Adoptions (Log Scale)")
    st.markdown("""
    <div style="background-color:#F0F8FF; padding:15px; border-radius:5px">
        <b>Applying a Log Scale</b><br>
        The previous graph shows a highly skewed distribution, with most states concentrated in 
        the lower range of charging station density. 
        A logarithmic transformation is applied to both axes to better capture variations 
        across a broader range of values. This adjustment reduces skewness and allows for a 
        clearer comparison of trends that may not be easily observed on a linear scale.
    </div>
    """, unsafe_allow_html=True)

    # Linear regression 
    fig_adoption = px.scatter(
        df_merged,
        x="Charging Stations per 10k (log)",
        y="EV Adoptions (log)",
        title="EV Charging Station Density vs. EV Adoptions (Log Scale)",
        labels={"Charging Stations per 10k (log)": "Charging Stations per 10K People (log)", "EV Adoptions (log)": "EV Adoptions (log)"},
        trendline="ols"
    )
    fig_adoption.update_traces(marker=dict(size=8, opacity=0.7, color="#4C72B0"))
    st.plotly_chart(fig_adoption, use_container_width=True)
    
    # Insights
    st.markdown("""
    <b>Key Insights: Log-Transformed EV Charging Station Density vs. EV Adoptions</b>
    <ul>
        <li>Applying a logarithmic transformation results in a more balanced distribution of charging station density and EV adoptions.</li>
        <li>The log scale makes it easier to distinguish variations among data points, particularly in the lower density range.</li>
        <li>An <b>Ordinary Least Squares (OLS) regression line</b> is included, with the following equation:</li>
    </ul>
    <div style="text-align: center; font-size: 16px; font-weight: bold; margin-top: -0.2cm; margin-bottom: 5px;">
        log(EV Adoptions) = 1.22154 × log(Charging Stations per 10K) + 8.89385</div>
    <ul>
        <li><b>Slope (1.22154)</b>: A 1% increase in log-transformed charging station density corresponds to a 1.22% increase in log-transformed EV adoptions. This suggests that while EV adoptions tend to increase as charging station density rises, the growth rate is not linear but rather gradual.</li>
        <li><b>Intercept (8.89385)</b>: Represents the expected log value of EV adoptions when the log-transformed charging station density is 0 (i.e., when there is one charging station).</li>
        <li><b>R² = 0.081166</b>: Even after log transformation, the coefficient of determination remains very low. This indicates that charging station density alone is insufficient to explain EV adoption numbers, suggesting that other factors, such as policies, economic conditions, and EV prices, likely play a significant role.</li>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")
    st.markdown("")
    
    # Data source & Abbreviations
    st.markdown("""
    <div style="font-size: 14px; color: gray;">
        <b>Acronyms and Abbreviations</b>: EV = Electric Vehicle  
        <br>
        <b>Source</b>: Vehicle Registration Counts by State (2023) from the Alternative Fuels Data Center (AFDC)
    </div>
    """, unsafe_allow_html=True)
    
    
elif menu_option == "EV Statistics II":    
    ###########################################################
    # 4. Electric Vehicles per 10,000 People (EV Density)
    ###########################################################
    st.header("Electric Vehicles per 10,000 People")
    @st.cache_data
    def load_map_data_ev10000():
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
        return pd.DataFrame(data)

    @st.cache_data
    def load_time_data_ev10000():
        try:
            df_ev_time = pd.read_csv("ev_per_10000.csv")
            return df_ev_time
        except Exception as e:
            st.error("Error loading ev_per_10000.csv: " + str(e))
            return pd.DataFrame()
    
    df_map_ev10000 = load_map_data_ev10000()
    df_time_ev10000 = load_time_data_ev10000()
    max_ev_10000 = df_map_ev10000["ev_per_10000"].max()
    
    # Create a dummy dataframe for a thin colorbar
    df_dummy = pd.DataFrame({
        "dummy_x": [0, 1],
        "dummy_y": [0, 1],
        "value":   [0, max_ev_10000]
    })
    
    # Adjust colorbar
    fig_colorbar = px.scatter(
        df_dummy,
        x="dummy_x",
        y="dummy_y",
        color="value",
        color_continuous_scale="Blues",
        range_color=(0, max_ev_10000)
    )
    fig_colorbar.update_traces(marker=dict(size=0), hovertemplate=None, hoverinfo="skip")
    fig_colorbar.update_xaxes(visible=False)
    fig_colorbar.update_yaxes(visible=False)
    fig_colorbar.update_layout(
        height=60,
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            orientation="h",
            x=0.54, 
            xanchor="center",
            y=0,
            yanchor="top",
            title=None 
        ),
        title=dict(
            text="<span style='color:gray; font-size:14px; font-weight:normal;'>EV per 10,000 People</span>",  
            x=0.055, 
            y=0.83,
            xanchor="left",
            yanchor="top"
        )
    )

    # Choropleth map for EV density
    fig_map_ev10000 = px.choropleth(
        df_map_ev10000,
        color="ev_per_10000",
        custom_data=["state", "ev_per_10000"],
        locationmode="USA-states",
        locations="state_code",
        scope="usa",
        color_continuous_scale="Blues",
        range_color=(0, max_ev_10000),
        labels={"ev_per_10000": "EV per 10,000 People"}
    )
    fig_map_ev10000.update_traces(
        hovertemplate="EV per 10,000 People<br>%{customdata[0]}: <b>%{customdata[1]}</b><extra></extra>"
    )
    fig_map_ev10000.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=380,
        width=600,
        coloraxis_showscale=False
    )

    # Bar chart for Top 10 states by EV density
    df_top10_ev10000 = df_map_ev10000.sort_values("ev_per_10000", ascending=False).head(10)
    fig_top10_ev10000 = px.bar(
        df_top10_ev10000,
        x="ev_per_10000",
        y="state",
        orientation="h",
        custom_data=["state", "ev_per_10000"],
        color="ev_per_10000",
        color_continuous_scale="Blues",
        range_color=(0, max_ev_10000),
        labels={"ev_per_10000": "EV per 10,000 People", "state": "State"}
    )
    fig_top10_ev10000.update_traces(
        hovertemplate="EV per 10,000 People<br>%{customdata[0]}: <b>%{customdata[1]}</b><extra></extra>"
    )
    fig_top10_ev10000.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(autorange="reversed"),
        bargap=0.35,
        height=400,
        coloraxis_showscale=False
    )
    fig_top10_ev10000.update_xaxes(
        showgrid=True,
        gridcolor="lightgray",
        gridwidth=1,
        griddash="dot"
    )

    # Layout for EV density section: two columns for map and bar chart, then the colorbar
    col1_ev, col2_ev = st.columns([1,1], gap="small")
    with col1_ev:
        st.write("#### 👥 EV Density by State per 10,000 People")
        st.plotly_chart(fig_map_ev10000, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
        
    with col2_ev:
        st.write("#### Top 10 States by EV per 10,000 People")
        st.plotly_chart(fig_top10_ev10000, use_container_width=True, config={"displayModeBar": False})
    st.plotly_chart(fig_colorbar, use_container_width=True, config={"displayModeBar": False})

    st.markdown("")
    st.markdown("")
    
    # Data source
    st.markdown("""
        <div style="font-size: 14px; color: gray;">
            <b>Source</b>: TransAtlas from the Alternative Fuels Data Center (AFDC)
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Comparison section for EV density
    st.header("⚖️ Comparison of EV per 10,000 People")
    selected_states_ev = st.multiselect(
        "Select up to 5 states to compare:",
        options=df_map_ev10000["state"].unique(),
        default=["California", "Washington", "Texas", "Florida", "New York"]
    )
    if len(selected_states_ev) > 5:
        st.error("Please select up to 5 states only.")
        selected_states_ev = selected_states_ev[:5]
    if not selected_states_ev:
        st.warning("Please select at least one state.")
    else:
        df_compare_ev = df_map_ev10000[df_map_ev10000["state"].isin(selected_states_ev)]
        fig_compare_ev = px.bar(
            df_compare_ev,
            x="state",
            y="ev_per_10000",
            labels={"state": "State", "ev_per_10000": "EV per 10,000 People"},
            color="ev_per_10000",
            color_continuous_scale="Blues",
            range_color=(0, max_ev_10000),
            hover_data=None
        )
        fig_compare_ev.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar=dict(
                orientation="v",
                len=1,
                thickness=16,
                x=1.05,
                xanchor="left",
                y=0.47,
                yanchor="middle",
                title="EV per 10,000 People"
            )
        )
        fig_compare_ev.update_traces(
            hovertemplate="EV per 10,000 People<br>%{x}: <b>%{y}</b><extra></extra>"
        )
        st.plotly_chart(fig_compare_ev, use_container_width=True, config={"displayModeBar": False})
        
    st.markdown("---")
    
    # Load data (Charging station data + EV registration data)
    @st.cache_data
    def load_ev_data():
        return pd.read_csv("EV_Station_Location.csv")

    @st.cache_data
    def load_ev_registration_data():
        return pd.read_csv("Population Estimate & EV Count.csv")

    @st.cache_data
    def load_ev_density_data():
        return pd.read_csv("ev_per_10000.csv")
    
    df_stations = load_ev_data()
    df_ev = load_ev_registration_data()
    df_density = load_ev_density_data()

    # Create a dictionary to convert state names to state codes
    us_state_abbreviations = {
        "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
        "colorado": "CO", "connecticut": "CT", "delaware": "DE", "district of columbia": "DC",
        "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID", "illinois": "IL",
        "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
        "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
        "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
        "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
        "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
        "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
        "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
        "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY"
    }

    # Convert state names to codes in EV density data
    df_density["State"] = df_density["state"].str.strip().str.lower().map(us_state_abbreviations)

    # Select population density data for year
    df_latest_density = df_density[df_density["year"] == df_density["year"].max()]

    # Calculate number of EV charging stations by state
    df_stations_count = df_stations.groupby("State").size().reset_index(name="Charging_Stations")

    # Clean column names in EV registration data
    df_ev = df_ev.rename(columns={"EV registration by state": "EV_Registrations", "2023": "Population"})
    df_ev = df_ev[df_ev["State"] != "US"]

    # Standardize State column (Convert to uppercase)
    df_stations_count["State"] = df_stations_count["State"].str.strip().str.upper()
    df_ev["State"] = df_ev["State"].str.strip().str.upper()
    df_latest_density["State"] = df_latest_density["State"].str.strip().str.upper()

    # Merge data based on state
    df_merged = pd.merge(df_stations_count, df_ev, on="State", how="inner")
    df_merged = pd.merge(df_merged, df_latest_density[["State", "ev_per_10000"]], on="State", how="inner")

    # Calculate charging station density per 10K people
    df_merged["Charging Stations per 10k"] = df_merged["Charging_Stations"] / (df_merged["Population"] / 10000)

    # Remove missing values
    df_merged = df_merged.dropna(subset=["Charging Stations per 10k", "ev_per_10000"])

    # Apply log transformation
    df_merged["Charging Stations per 10k (log)"] = np.log1p(df_merged["Charging Stations per 10k"])
    df_merged["log_EV_Registrations"] = np.log1p(df_merged["EV_Registrations"])
    df_merged["EV per 10000 (log)"] = np.log1p(df_merged["ev_per_10000"])

    # Research Question 2: EV Charging Station Density vs Population Density
    st.header("EV Charging Station Density vs. Population Density (Log Scale)")
    fig_population = px.scatter(
        df_merged,
        x="EV per 10000 (log)",
        y="Charging Stations per 10k (log)",
        title="EV Charging Station Density vs. Population Density (Log Scale)",
        labels={"EV per 10000 (log)": "EVs per 10K People (log)", "Charging Stations per 10k (log)": "Charging Stations per 10K People (log)"},
        trendline="ols"
    )
    fig_population.update_traces(marker=dict(size=8, opacity=0.7, color="#4C72B0"))
    st.plotly_chart(fig_population, use_container_width=True)

    # Insights
    st.markdown("""
    <b>Key Insights: EV Charging Station Density vs. Population Density (Log Scale)</b>
    <ul>
        <li>This graph illustrates the relationship between <b>population density (log-scale)</b> and <b>EV charging station density (log-scale)</b>.</li>
        <li>An <b>Ordinary Least Squares (OLS) regression analysis</b> is performed, yielding the following equation:</li>
    </ul>
    <div style="text-align: center; font-size: 16px; font-weight: bold; margin-top: -0.2cm; margin-bottom: 5px;">
        Charging Stations per 10K People (log) = 0.330674 × EVs per 10K People (log) − 0.409718
    </div>
    <ul>
        <li><b>Slope (0.330674)</b>: A 1% increase in log-transformed EV density corresponds to a 0.33% increase in log-transformed charging station density. Since the slope is less than 1, this suggests that the growth rate of charging stations is lower than that of EVs, indicating that EV adoption may be outpacing charging infrastructure expansion.</li>
        <li><b>Intercept (-0.409718)</b>: Represents the expected log value of charging station density when log-transformed EV density is 0 (i.e., when there is only one EV). This suggests that a baseline level of charging infrastructure may still exist even in areas with very low EV density.</li>
        <li><b>R² = 0.489790</b>: While this R² value indicates a moderate correlation, it is not close to 1, implying that additional factors such as policies, economic conditions, or regional infrastructure strategies likely play a role in determining charging station density.</li>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")
    st.markdown("")

    # Data source & Abbreviations
    st.markdown("""
    <div style="font-size: 14px; color: gray;">
        <b>Acronyms and Abbreviations</b>: EV = Electric Vehicle  
        <br>
        <b>Source</b>: TransAtlas from the Alternative Fuels Data Center (AFDC)
    </div>
    """, unsafe_allow_html=True)


# Conclusion page
elif menu_option == "Conclusion":
    st.write("#### Conclusion & Critical Analysis")
    st.markdown("""
        <div style="padding-bottom: 4px;">
        This project provides a comprehensive visualization of public EV charging infrastructure and its role in electric vehicle adoption and accessibility across the U.S. 
        The interactive maps and statistical analyses clearly illustrate the distribution of charging stations, their accessibility relative to population density, 
        and the relationships with EV adoption rates and gasoline price volatility.  
    <ul>
    <br>
        <b>EV Charging Station Distribution</b>
        <li>EV registrations in the U.S. show significant geographic concentration, with California leading by a large margin.</li>
        <li>Wide disparities exist across states, suggesting factors such as state policies, economic conditions, and infrastructure availability strongly influence regional EV adoption patterns.</li>
    <br>
        <b>EV Charging Station Infrastructure Growth & Gasoline Prices</b>
        <li>U.S. public EV charging infrastructure has shown consistent and rapid growth, particularly since 2011, with charging ports increasing faster than station locations, indicating a shift toward multi-port stations.</li>
        <li>Gasoline price trends from 2007 to 2023 show significant fluctuations driven by economic crises, global energy disruptions, and supply chain issues, potentially influencing consumer decisions towards adopting electric vehicles.</li>
    <br>
        <b>EV Charging Station Density vs. EV Adoptions (Log Scale)</b>
        <li>Log transformation provides a more balanced view of the relationship between charging station density and EV adoption.</li>
        <li>While EV adoptions generally increase as charging station density grows, the rate of increase is gradual rather than linear.</li>
        <li>A low R² value (~0.08) indicates that charging station density alone does not sufficiently explain EV adoption rates; thus, additional factors such as policies, economic conditions, and consumer behavior should be considered.</li>
    <br>
        <b>EV Charging Station Density vs. Population Density (Log Scale)</b>
        <li>In the U.S., states with higher EV adoption generally tend to have a higher density of EV charging stations.</li>
        <li>However, with a coefficient of determination of approximately 49%, while the relationship between the two variables is relatively strong, it also suggests that other factors may still influence charging station density.</li>      
    </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Limitations
    st.markdown("---")
    st.write("#### Limitations")
    st.markdown("""
    <ul>
        <li>The current analysis has primarily relied on aggregated state-level data, potentially masking important local variations and nuances.</li>
        <li>The weak to moderate correlations (indicated by relatively low R² values) suggest that EV adoption and infrastructure expansion are influenced by various factors beyond the scope of the current data, such as local policies, incentives, consumer awareness, and socioeconomic conditions.</li>      
        <li>The current analysis includes only public EV charging stations, excluding private and residential charging options. Due to the omission of private charging facilities, the dataset may underestimate the actual availability and accessibility of EV charging across states.</li>
    </ul>
    """, unsafe_allow_html=True)
    
    # Potential Improvements & Future Directions
    st.markdown("---")
    st.write("#### Potential Improvements & Future Directions")
    st.markdown("""
    <ul>
        <li>Incorporate granular, local-level data to better capture nuances in EV adoption and charging infrastructure accessibility that state-level data might obscure.</li>
        <li>Integrate additional influencing variables such as local policies, economic incentives, consumer demographics, and socioeconomic factors to improve explanatory power and deepen the understanding of EV adoption drivers.</li>
        <li>Expand the dataset to include private and residential EV charging stations, providing a more accurate assessment of the true availability and accessibility of charging infrastructure.</li>      
    </ul>
    """, unsafe_allow_html=True)
    

# Improve Dashboard UI (Apply CSS)
st.markdown("""
    <style>
        .title-text { font-size: 36px !important; font-weight: bold; text-align: center; color: #1E88E5; }
        .subtitle-text { font-size: 22px !important; font-weight: bold; color: #1E88E5; margin-bottom: 5px; }
        .dataframe { background-color: #F8F9FA; border-radius: 10px; padding: 10px; }
        .stSlider > div { background-color: #E3F2FD; border-radius: 8px; padding: 5px; }
    </style>
""", unsafe_allow_html=True)
