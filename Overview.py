"""
NHS GP Appointments Forecasting Dashboard
==========================================
Multi-level forecasting dashboard for NHS GP appointments.

Author: NHS Forecasting Team
Date: March 2026
"""

import streamlit as st
import pandas as pd
import json

# Page configuration
st.set_page_config(
    page_title="NHS GP Forecasting Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("🏥 NHS GP Appointments Forecasting Dashboard")
st.markdown("---")

# Introduction
st.markdown("""
### Welcome to the NHS GP Appointments Forecasting Platform

This dashboard provides **multi-level forecasting** for GP appointments across England:
- **Sub-ICB Level**: 106 locations using Holt-Winters models
- **Practice Level**: 1,101 London GP practices Holt-Winters forecasting model

Use the sidebar to navigate between different views. ↖️
""")

# Load metadata
@st.cache_data(ttl=3600)
def load_metadata():
    """Load forecasting metadata"""
    try:
        # Sub-ICB metadata
        with open('./outputs/metadata.json', 'r') as f:
            sub_icb_meta = json.load(f)
        
        # Practice metadata
        with open('./outputs/practice_forecasting_metadata.json', 'r') as f:
            practice_meta = json.load(f)
        
        return sub_icb_meta, practice_meta
    except:
        return None, None

sub_icb_meta, practice_meta = load_metadata()

# Display key metrics in columns
st.markdown("### 📊 Dashboard Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🏢 Sub-ICB Level")
    if sub_icb_meta:
        st.metric("Locations Forecasted", "106 Sub-ICBs")
        st.metric("Model Type", "Holt-Winters")
        st.info("**Forecast Period:** Feb 2026 - Jan 2027 (12 months)")
    else:
        st.info("Sub-ICB forecasting complete")

with col2:
    st.markdown("#### 🏥 Practice Level")
    if practice_meta:
        st.metric("London Practices", f"{practice_meta['metadata']['total_practices']:,}")
        st.metric("Model Type", "Holt-Winters")
        st.metric("Median MAPE", f"{practice_meta['model_performance']['median_mape']:.1f}%")
    else:
        st.info("Practice forecasting complete")

with col3:
    st.markdown("#### 👥 Resource Planning")
    if practice_meta:
        total_fte = practice_meta['fte_summary']['total_fte_avg']
        st.metric("Total London FTE Needed", f"{total_fte:,.0f}")
        st.metric("Avg FTE per Practice", f"{practice_meta['fte_summary']['avg_fte_per_practice']:.1f}")
        st.info("**Capacity:** GP 525/mo, Staff 630/mo")
    else:
        st.info("FTE calculations available")

st.markdown("---")

# Quick navigation
st.markdown("### 🧭 Quick Navigation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 📍 Sub-ICB View
    - View forecasts for 106 Sub-ICB locations
    
    👉 **Navigate to:** `Sub-ICB View` in the sidebar
    """)

with col2:
    st.markdown("""
    #### 🏥 Practice Analysis
    - Appoitment forecasts for London GP practices
    - FTE requirements and resource planning
    - Model performance metrics
    
    👉 **Navigate to:** `Practice Analysis` in the sidebar
    """)

st.markdown("---")

# Footer
st.markdown("""
### 📚 About This Dashboard
            
**Author**:
- Created by Joseph Gayle, as an exploratory project

**Data Sources:**
- NHS GP Appointment - Historical data: October 2022 - January 2026 (40 months)
- https://digital.nhs.uk/services/gp-appointment-data
- Training set: October 2022 - July 2025 (34 months)
- Test set: August 2025 - January 2026 (6 months)
- Forecast period: February 2026 - January 2027 (12 months)

**Models:**
- Holt-Winters Triple Exponential Smoothing (m=12)

**Capacity Assumptions:**
- GP: 25 appointments/day @ 100% utilization = 525/month
- Practice Staff: 30 appointments/day @ 100% utilization = 630/month

**Assumptions=:**
- ICB and Practice-level models validated with 6-month hold-out period
- Holt-Winters captures seasonal patterns with trend and seasonality components
- Top 95% of practices retained based on MAPE performance 
- Unknown appointments (e.g. attended or DNA unspecified) were removed from this analysis (~30%)
- Unknown appointements with a specifed outcome (attended/DNA) were retained in this dataset
""")

