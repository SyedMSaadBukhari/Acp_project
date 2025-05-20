import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Reuse the cached data
import importlib
page_1 = importlib.import_module("pages.1_Data_Overview")
load_data = page_1.load_data

df = load_data()

st.title("COVID-19 Detailed Analysis")

# Create filters
col1, col2 = st.columns(2)

with col1:
    # Multi-select for countries
    # Filter out 'World' and continents from the location list
    countries = sorted([loc for loc in df['location'].unique() 
                       if loc not in ['World'] and 
                       (not pd.isna(loc)) and 
                       (loc not in df['continent'].unique())])
    
    selected_countries = st.multiselect(
        "Select Countries to Compare",
        countries,
        default=countries[:5] if len(countries) > 5 else countries
    )

with col2:
    # Select metric to analyze
    metrics = {
        'New Cases (7-day avg)': 'new_cases_smoothed',
        'New Deaths (7-day avg)': 'new_deaths_smoothed',
        'Total Cases per Million': 'total_cases_per_million',
        'Total Deaths per Million': 'total_deaths_per_million',
        'ICU Patients per Million': 'icu_patients_per_million',
        'Hospital Patients per Million': 'hosp_patients_per_million',
        'Vaccination Rate (%)': 'people_fully_vaccinated_per_hundred'
    }
    selected_metric = st.selectbox("Select Metric to Analyze", list(metrics.keys()))

# Filter data based on selection
filtered_df = df[df['location'].isin(selected_countries)]

# Create visualizations
st.subheader("Comparative Analysis")

# Line chart comparing countries over time
fig1 = px.line(
    filtered_df,
    x='date',
    y=metrics[selected_metric],
    color='location',
    title=f'{selected_metric} - Country Comparison',
    labels={metrics[selected_metric]: selected_metric}
)
st.plotly_chart(fig1)

# Latest statistics
st.subheader("Latest Statistics")

# Get the latest data for each country
latest_data = (filtered_df.sort_values('date')
               .groupby('location')
               .last()
               .reset_index())

# Bar chart of latest values
fig2 = px.bar(
    latest_data,
    x='location',
    y=metrics[selected_metric],
    title=f'Latest {selected_metric} by Country',
    labels={metrics[selected_metric]: selected_metric}
)
st.plotly_chart(fig2)

# Correlation Analysis
st.subheader("Correlation Analysis")

correlation_metrics = {
    'total_cases_per_million': 'Total Cases per Million',
    'total_deaths_per_million': 'Total Deaths per Million',
    'icu_patients_per_million': 'ICU Patients per Million',
    'people_fully_vaccinated_per_hundred': 'Vaccination Rate (%)'
}

# Calculate correlations for selected countries
latest_corr_data = latest_data[list(correlation_metrics.keys())].corr()

# Create heatmap
fig3 = go.Figure(data=go.Heatmap(
    z=latest_corr_data,
    x=list(correlation_metrics.values()),
    y=list(correlation_metrics.values()),
    colorscale='RdBu'
))
fig3.update_layout(
    title='Correlation between Different COVID-19 Metrics',
    height=500
)
st.plotly_chart(fig3)

# Add summary statistics
st.subheader("Summary Statistics")
summary_df = filtered_df.groupby('location')[metrics[selected_metric]].agg(['mean', 'min', 'max', 'std']).round(2)
summary_df.columns = ['Mean', 'Minimum', 'Maximum', 'Std Dev']
st.dataframe(summary_df)
