import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Reuse the cached data
import importlib
page_1 = importlib.import_module("pages.1_Data_Overview")
load_data = page_1.load_data

df = load_data()

st.title("Global COVID-19 Summary Analysis")

# Calculate global statistics (excluding continents and World)
global_df = df[
    ~df['location'].isin(df['continent'].unique()) & 
    (df['location'] != 'World')
]

global_stats = global_df.groupby('date').agg({
    'new_cases': 'sum',
    'new_deaths': 'sum',
    'people_fully_vaccinated': 'sum',
    'icu_patients': 'sum'
}).reset_index()

# Time range selector
date_range = st.date_input(
    "Select Date Range",
    value=(global_stats['date'].min().date(), global_stats['date'].max().date()),
    min_value=global_stats['date'].min().date(),
    max_value=global_stats['date'].max().date()
)

# Filter based on date range
filtered_stats = global_stats[
    (global_stats['date'].dt.date >= date_range[0]) &
    (global_stats['date'].dt.date <= date_range[1])
]

# Display global totals
st.subheader("Global Overview")
latest_global = filtered_stats.iloc[-1]
total_cases = filtered_stats['new_cases'].sum()
total_deaths = filtered_stats['new_deaths'].sum()

cols = st.columns(4)
with cols[0]:
    st.metric("Total Cases", f"{total_cases:,.0f}")
with cols[1]:
    st.metric("Total Deaths", f"{total_deaths:,.0f}")
with cols[2]:
    st.metric("Death Rate", f"{(total_deaths/total_cases*100):.2f}%")
with cols[3]:
    st.metric("Current ICU Patients", f"{latest_global['icu_patients']:,.0f}")

# Global trends
st.subheader("Global Trends")
tab1, tab2, tab3 = st.tabs(["Cases & Deaths", "Vaccination Progress", "Regional Analysis"])

with tab1:
    # Cases and deaths trend
    fig1 = px.line(
        filtered_stats,
        x='date',
        y=['new_cases', 'new_deaths'],
        title='Global Daily Cases and Deaths',
        labels={'value': 'Count', 'variable': 'Metric'}
    )
    st.plotly_chart(fig1)

with tab2:
    # Vaccination progress for top countries
    latest_vax = df.groupby('location').agg({
        'people_fully_vaccinated_per_hundred': 'last',
        'population': 'last'
    }).sort_values('people_fully_vaccinated_per_hundred', ascending=False)
    
    fig2 = px.bar(
        latest_vax.head(20).reset_index(),
        x='location',
        y='people_fully_vaccinated_per_hundred',
        title='Vaccination Rate by Country (Top 20)',
        labels={'people_fully_vaccinated_per_hundred': 'Population Fully Vaccinated (%)'}
    )
    st.plotly_chart(fig2)

with tab3:
    # Regional analysis
    if 'continent' in df.columns:
        continental_data = df[df['continent'].notna()].groupby(['continent', 'date']).agg({
            'new_cases': 'sum',
            'new_deaths': 'sum'
        }).reset_index()
        
        fig3 = px.line(
            continental_data,
            x='date',
            y='new_cases',
            color='continent',
            title='Cases by Continent',
            labels={'new_cases': 'New Cases'}
        )
        st.plotly_chart(fig3)

# Add key insights
st.subheader("Key Insights")

# Calculate some interesting statistics
peak_cases_date = filtered_stats.loc[filtered_stats['new_cases'].idxmax(), 'date'].strftime('%Y-%m-%d')
peak_cases = filtered_stats['new_cases'].max()
peak_deaths_date = filtered_stats.loc[filtered_stats['new_deaths'].idxmax(), 'date'].strftime('%Y-%m-%d')
peak_deaths = filtered_stats['new_deaths'].max()

insights = [
    f"🔹 Peak daily cases: {peak_cases:,.0f} on {peak_cases_date}",
    f"🔹 Peak daily deaths: {peak_deaths:,.0f} on {peak_deaths_date}",
    f"🔹 Average daily cases: {filtered_stats['new_cases'].mean():,.0f}",
    f"🔹 Average daily deaths: {filtered_stats['new_deaths'].mean():,.0f}"
]

for insight in insights:
    st.markdown(insight)
