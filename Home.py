import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="COVID-19 Data Dashboard",
    page_icon="🦠",
    layout="wide"
)

st.title("COVID-19 Global Data Dashboard")

# Load the data to show some quick stats
@st.cache_data
def load_data():
    df = pd.read_csv("data/covid_data.csv")
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Fill missing values with 0 for numeric columns
    numeric_columns = ['new_cases', 'new_deaths', 'total_cases', 'total_deaths']
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    return df

df = load_data()

# Calculate some quick global stats
latest_date = df['date'].max()
total_cases = df.groupby('date')['new_cases'].sum().sum()
total_deaths = df.groupby('date')['new_deaths'].sum().sum()
countries_count = df['location'].nunique()

st.markdown("""
## About this Dashboard
This interactive dashboard provides comprehensive visualizations and analysis of COVID-19 data 
from around the world. The data is sourced from Our World in Data and is regularly updated.

### Quick Global Statistics:
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Cases", f"{total_cases:,.0f}")
with col2:
    st.metric("Total Deaths", f"{total_deaths:,.0f}")
with col3:
    st.metric("Countries Tracked", f"{countries_count:,}")

st.markdown("""
### Dashboard Features:
🔍 **Data Overview**
- Country-specific COVID-19 trends
- Daily cases and deaths
- Vaccination progress tracking
- Key health metrics

📊 **Detailed Analysis**
- Multi-country comparisons
- Time series analysis
- Correlation between different metrics
- Statistical summaries

📈 **Summary Analysis**
- Global trends and patterns
- Continental breakdowns
- Vaccination progress by region
- Key insights and highlights

### How to Use:
1. Use the sidebar to navigate between different pages
2. Select countries and date ranges to filter data
3. Interact with charts to zoom, pan, and hover for details
4. Download data and visualizations using the export options

### Data Sources:
- Our World in Data (OWID) COVID-19 Dataset
- Last Updated: {}
""".format(latest_date.strftime('%Y-%m-%d')))


st.markdown("---")
st.markdown("*Data provided by Our World in Data (OWID).*")
