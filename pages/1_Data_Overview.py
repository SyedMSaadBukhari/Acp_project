import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Cache the data loading
@st.cache_data
def load_data():
    df = pd.read_csv("data/covid_data.csv")
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Fill missing values with 0 for numeric columns
    numeric_columns = ['new_cases', 'new_deaths', 'total_cases', 'total_deaths', 
                      'icu_patients', 'total_vaccinations', 'people_fully_vaccinated',
                      'people_fully_vaccinated_per_hundred', 'total_tests_per_thousand']
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Create smoothed columns if they don't exist
    if 'new_cases_smoothed' not in df.columns:
        df['new_cases_smoothed'] = df.groupby('location')['new_cases'].rolling(7).mean().reset_index(0, drop=True)
    if 'new_deaths_smoothed' not in df.columns:
        df['new_deaths_smoothed'] = df.groupby('location')['new_deaths'].rolling(7).mean().reset_index(0, drop=True)
    
    return df

# Load the data
df = load_data()

st.title("COVID-19 Data Overview")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Interactive Filter Section")
    
    # Country selection
    countries = sorted(df['location'].unique())
    selected_country = st.selectbox("Select Country:", countries)
    
    # Date range selection with default values
    default_end_date = df['date'].max()
    default_start_date = default_end_date - timedelta(days=30)  # Last 30 days by default
    
    start_date = st.date_input(
        "Start Date",
        value=default_start_date,
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date()
    )
    
    end_date = st.date_input(
        "End Date",
        value=default_end_date,
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date()
    )
    
    # Filter data based on inputs
    filtered_df = df[
        (df['location'] == selected_country) &
        (df['date'].dt.date >= start_date) &
        (df['date'].dt.date <= end_date)
    ]
    
    # Cases trend visualization
    fig1 = px.line(
        filtered_df, 
        x='date', 
        y=['new_cases_smoothed', 'new_deaths_smoothed'],
        title=f'COVID-19 Cases and Deaths Trend in {selected_country}',
        labels={'value': 'Count', 'variable': 'Metric'},
    )
    st.plotly_chart(fig1)

with col2:
    st.subheader("Vaccination Progress")
    
    # Latest vaccination data for selected country
    latest_vax_data = filtered_df.iloc[-1] if not filtered_df.empty else pd.Series()
    
    # Display vaccination metrics
    st.metric(
        "Total Vaccinations", 
        f"{latest_vax_data.get('total_vaccinations', 0):,.0f}" if pd.notna(latest_vax_data.get('total_vaccinations')) else "No data"
    )
    
    st.metric(
        "People Fully Vaccinated",
        f"{latest_vax_data.get('people_fully_vaccinated', 0):,.0f}" if pd.notna(latest_vax_data.get('people_fully_vaccinated')) else "No data"
    )
    
    # Vaccination trend
    fig2 = px.area(
        filtered_df,
        x='date',
        y='people_fully_vaccinated_per_hundred',
        title=f'Vaccination Progress in {selected_country} (% of population)',
        labels={'people_fully_vaccinated_per_hundred': 'Fully Vaccinated (%)'}
    )
    st.plotly_chart(fig2)

# Additional metrics at the bottom
st.subheader("Key Statistics")
cols = st.columns(4)

with cols[0]:
    st.metric(
        "Total Cases",
        f"{latest_vax_data.get('total_cases', 0):,.0f}" if pd.notna(latest_vax_data.get('total_cases')) else "No data"
    )
with cols[1]:
    st.metric(
        "Total Deaths",
        f"{latest_vax_data.get('total_deaths', 0):,.0f}" if pd.notna(latest_vax_data.get('total_deaths')) else "No data"
    )
with cols[2]:
    st.metric(
        "ICU Patients",
        f"{latest_vax_data.get('icu_patients', 0):,.0f}" if pd.notna(latest_vax_data.get('icu_patients')) else "No data"
    )
with cols[3]:
    st.metric(
        "Tests per Thousand",
        f"{latest_vax_data.get('total_tests_per_thousand', 0):,.1f}" if pd.notna(latest_vax_data.get('total_tests_per_thousand')) else "No data"
    )
