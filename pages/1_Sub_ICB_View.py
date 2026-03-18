"""
NHS GP Appointments Forecasting Dashboard - Sub-ICB View
=========================================================
Interactive dashboard for viewing appointment forecasts by Sub-ICB location.

Forecast Model: Holt-Winters (Triple Exponential Smoothing), seasonal period m=12
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Sub-ICB Forecast",
    page_icon="🏥",
    layout="wide"
)

# Title and description
st.title("🏥 Sub-ICB Appointments Forecasting")
st.markdown("""
This dashboard displays appointment forecasts for NHS Sub-ICB locations using the **Holt-Winters forecasting model**.
- **Historical Period**: August 2023 - January 2026 (30 months)
- **Forecast Period**: February 2026 - January 2027 (12 months)
- **Model**: Holt-Winters Triple Exponential Smoothing (m=12)
- **Locations**: 106 Sub-ICBs across 7 regions
""")

# Load data
@st.cache_data(ttl=3600, show_spinner="Loading Sub-ICB data...")
def load_data():
    """Load historical and forecast data"""
    historical = pd.read_csv('./outputs/historical_monthly_sub_icb.csv')
    forecast = pd.read_csv('./outputs/forecast_production.csv')
    
    # Convert Month to datetime
    historical['Month'] = pd.to_datetime(historical['Month'])
    forecast['Month'] = pd.to_datetime(forecast['Month'])
    
    return historical, forecast

# Load the data
try:
    df_historical, df_forecast = load_data()
    
    # Sidebar - Sub-ICB selection
    st.sidebar.header("📍 Location Selection")
    
    # Get unique Sub-ICB locations
    sub_icbs = sorted(df_historical['SUB_ICB_NAME'].unique())
    
    # Dropdown for Sub-ICB selection
    selected_sub_icb = st.sidebar.selectbox(
        "Select Sub-ICB Location:",
        sub_icbs,
        index=0
    )
    
    # Filter data for selected Sub-ICB
    hist_filtered = df_historical[df_historical['SUB_ICB_NAME'] == selected_sub_icb].copy()
    forecast_filtered = df_forecast[df_forecast['SUB_ICB_NAME'] == selected_sub_icb].copy()
    
    # Sort by date
    hist_filtered = hist_filtered.sort_values('Month')
    forecast_filtered = forecast_filtered.sort_values('Month')
    
    # Display location info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Selected Location:**  \n{selected_sub_icb}")
    
    if len(hist_filtered) > 0:
        region = hist_filtered['REGION_NAME'].iloc[0]
        region_code = hist_filtered['REGION_CODE'].iloc[0]
        st.sidebar.markdown(f"**Region:** {region} ({region_code})")
    
    # Main content - Forecast visualization
    st.header(f"📊 Appointment Forecast: {selected_sub_icb}")
    
    # Create the time series chart
    fig = go.Figure()
    
    # Add historical data
    fig.add_trace(go.Scatter(
        x=hist_filtered['Month'],
        y=hist_filtered['Appointments'],
        mode='lines+markers',
        name='Historical Data',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    
    # Add forecast data - include last historical point for seamless connection
    if len(hist_filtered) > 0 and len(forecast_filtered) > 0:
        # Get the last historical point
        last_hist_date = hist_filtered['Month'].iloc[-1]
        last_hist_value = hist_filtered['Appointments'].iloc[-1]
        
        # Prepend to forecast data for continuous line
        forecast_dates = pd.concat([pd.Series([last_hist_date]), forecast_filtered['Month']]).reset_index(drop=True)
        forecast_values = pd.concat([pd.Series([last_hist_value]), forecast_filtered['Forecast_Appointments']]).reset_index(drop=True)
        
        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=forecast_values,
            mode='lines+markers',
            name='Holt-Winters Forecast',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=6, symbol='diamond')
        ))
    else:
        # Fallback if no historical data
        fig.add_trace(go.Scatter(
            x=forecast_filtered['Month'],
            y=forecast_filtered['Forecast_Appointments'],
            mode='lines+markers',
            name='Holt-Winters Forecast',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=6, symbol='diamond')
        ))
    
    # Add vertical line to separate historical from forecast
    if len(forecast_filtered) > 0:
        first_forecast_date = forecast_filtered['Month'].min()
        fig.add_shape(
            type="line",
            x0=first_forecast_date, x1=first_forecast_date,
            y0=0, y1=1,
            yref="paper",
            line=dict(color="gray", width=2, dash="dot")
        )
        # Add annotation for the vertical line
        fig.add_annotation(
            x=first_forecast_date,
            y=1.0,
            yref="paper",
            text="Forecast Start",
            showarrow=False,
            yshift=10
        )
    
    # Update layout
    fig.update_layout(
        title=f"Monthly Appointments: {selected_sub_icb}",
        xaxis_title="Month",
        yaxis_title="Number of Appointments",
        hovermode='x unified',
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Historical Average (Monthly)",
            f"{hist_filtered['Appointments'].mean():,.0f}"
        )
    
    with col2:
        st.metric(
            "Forecast Average (Monthly)",
            f"{forecast_filtered['Forecast_Appointments'].mean():,.0f}"
        )
    
    with col3:
        total_forecast = forecast_filtered['Forecast_Appointments'].sum()
        st.metric(
            "Total Forecast (12 Months)",
            f"{total_forecast:,.0f}"
        )
    
    with col4:
        if len(hist_filtered) > 0 and len(forecast_filtered) > 0:
            pct_change = ((forecast_filtered['Forecast_Appointments'].mean() / hist_filtered['Appointments'].mean()) - 1) * 100
            st.metric(
                "Average Change",
                f"{pct_change:+.1f}%"
            )
    
    # Optional: Show data table
    with st.expander("📋 View Forecast Data Table"):
        st.subheader("Forecast Details")
        display_df = forecast_filtered[['Month', 'Forecast_Appointments']].copy()
        display_df['Month'] = display_df['Month'].dt.strftime('%B %Y')
        display_df.columns = ['Month', 'Forecasted Appointments']
        display_df['Forecasted Appointments'] = display_df['Forecasted Appointments'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

except FileNotFoundError as e:
    st.error(f"""
    ⚠️ **Data files not found!**
    
    Please ensure the following files exist in the `./outputs/` directory:
    - `historical_monthly_sub_icb.csv`
    - `forecast_production.csv`
    
    Error: {str(e)}
    """)
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.exception(e)
