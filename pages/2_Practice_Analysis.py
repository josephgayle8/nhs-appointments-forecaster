"""
NHS GP Practice-Level Forecasting Dashboard
============================================
Detailed analysis and forecasting for individual London GP practices.

Model: Holt-Winters Exponential Smoothing (m=12)
Practices: 1,046 London GP practices
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Practice Analysis",
    page_icon="🏥",
    layout="wide"
)

# Title
st.title("🏥 London GP Practice-Level Analysis")
st.markdown("""
Detailed forecasting and resource planning for **London GP practices** using Holt-Winters forecasting model.
- **Historical Period**: October 2022 - January 2026 (40 months)
- **Forecast Period**: February 2026 - January 2027 (12 months)
- **Model**: Holt-Winters Exponential Smoothing (m=12)
- **Evaluation**: Test set 6-month period (Aug 2025 - Jan 2026)
""")

st.markdown("---")

# Load data
@st.cache_data(ttl=3600, show_spinner="Loading practice data...")
def load_practice_data():
    """Load practice-level forecasting data"""
    # Load validation results (Holt-Winters forecasting model validation)
    df_validation = pd.read_csv('./outputs/practice_sarima_validation_successful.csv')
    
    # Load London GP lookup to get practice names and locations
    df_lookup = pd.read_csv('./outputs/london_gp_lookup.csv')
    
    # Merge validation results with lookup data
    df_metadata = df_validation.merge(
        df_lookup[['GP_CODE', 'GP_NAME', 'ICB_CODE', 'ICB_NAME', 
                   'SUB_ICB_LOCATION_CODE', 'SUB_ICB_LOCATION_NAME']],
        on='GP_CODE',
        how='left'
    )
    
    # Rename MAPE column for consistency with existing code
    df_metadata = df_metadata.rename(columns={'MAPE': 'Validation_MAPE'})
    
    # Forecast data (historical + validation + forecast) - using existing file
    df_forecast = pd.read_csv('./outputs/practice_forecast_total.csv')
    df_forecast['Month'] = pd.to_datetime(df_forecast['Month'])
    
    # Filter forecast data to only include practices in the validation results
    df_forecast = df_forecast[df_forecast['GP_CODE'].isin(df_metadata['GP_CODE'])]
    
    # FTE requirements - using existing file
    df_fte = pd.read_csv('./outputs/practice_fte_requirements.csv')
    df_fte['Month'] = pd.to_datetime(df_fte['Month'])
    
    # Filter FTE data to only include practices in the validation results
    df_fte = df_fte[df_fte['GP_CODE'].isin(df_metadata['GP_CODE'])]
    
    # Load or create metadata JSON
    try:
        with open('./outputs/practice_forecasting_metadata.json', 'r') as f:
            metadata = json.load(f)
    except FileNotFoundError:
        # Create basic metadata from validation results
        metadata = {
            'metadata': {
                'total_practices': len(df_metadata),
                'model': 'Holt-Winters',
                'validation_period': '6 months (Aug 2025 - Jan 2026)',
                'forecast_period': '12 months (Feb 2026 - Jan 2027)'
            },
            'model_performance': {
                'median_mape': df_metadata['Validation_MAPE'].median(),
                'mean_mape': df_metadata['Validation_MAPE'].mean(),
                'median_rmse': df_metadata['RMSE'].median()
            }
        }
    
    return df_metadata, df_forecast, df_fte, metadata

try:
    df_metadata, df_forecast, df_fte, metadata = load_practice_data()
    
    # ============================================================================
    # LONDON-WIDE OVERVIEW - Moved to top for better visibility
    # ============================================================================
    st.header("📈 London-Wide Overview")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Forecast Growth Leaders", "🏆 Top Practices by FTE", "📊 Model Performance", "🗺️ Geographic Distribution"])
    
    # Cache expensive forecast growth calculation
    @st.cache_data(ttl=3600, show_spinner=False)
    def calculate_forecast_growth(df_forecast, df_metadata):
        """Calculate forecast growth for all practices"""
        forecast_growth_data = []
        
        for gp_code in df_metadata['GP_CODE'].unique():
            # Get historical data (Type = 'Historical')
            hist_data = df_forecast[(df_forecast['GP_CODE'] == gp_code) & 
                                     (df_forecast['Type'] == 'Historical')]
            
            # Get forecast data (Type = 'Forecast')
            fcst_data = df_forecast[(df_forecast['GP_CODE'] == gp_code) & 
                                     (df_forecast['Type'] == 'Forecast')]
            
            if len(hist_data) > 0 and len(fcst_data) > 0:
                avg_hist = hist_data['Total_Appointments'].mean()
                avg_fcst = fcst_data['Total_Appointments'].mean()
                
                if avg_hist > 0:
                    pct_change = ((avg_fcst / avg_hist) - 1) * 100
                    
                    # Get practice info
                    practice_info_temp = df_metadata[df_metadata['GP_CODE'] == gp_code].iloc[0]
                    
                    forecast_growth_data.append({
                        'GP_CODE': gp_code,
                        'GP_NAME': practice_info_temp['GP_NAME'],
                        'ICB_NAME': practice_info_temp['ICB_NAME'],
                        'Avg_Historical': avg_hist,
                        'Avg_Forecast': avg_fcst,
                        'Forecast_Change_Pct': pct_change,
                        'Absolute_Change': avg_fcst - avg_hist
                    })
        
        return pd.DataFrame(forecast_growth_data)
    
    with tab1:
        st.subheader("Top 30 Practices by Forecast Growth")
        st.markdown("""
        **Forecast Change (%)** shows the expected year-over-year growth:
        """)
        # - Formula: `((Avg Forecast / Avg Historical) - 1) × 100`
        # - **Positive %**: Practice expects more appointments than historical average
        # - **Negative %**: Practice expects FEWER appointments than historical average
        
        # Calculate forecast change using cached function
        df_growth = calculate_forecast_growth(df_forecast, df_metadata)
        
        # Get top 30 by forecast change percentage
        top30_growth = df_growth.nlargest(30, 'Forecast_Change_Pct')
        
        # Create horizontal bar chart
        fig_growth = px.bar(
            top30_growth,
            y='GP_NAME',
            x='Forecast_Change_Pct',
            orientation='h',
            title="Top 30 Practices by Expected Year-over-Year Growth",
            labels={
                'Forecast_Change_Pct': 'Forecast Change (%)', 
                'GP_NAME': 'Practice'
            },
            color='Forecast_Change_Pct',
            color_continuous_scale='RdYlGn',
            hover_data={
                'GP_NAME': False,
                'Forecast_Change_Pct': ':.1f',
                'Avg_Historical': ':,.0f',
                'Avg_Forecast': ':,.0f',
                'Absolute_Change': ':+,.0f'
            }
        )
        
        fig_growth.update_layout(
            height=800,
            showlegend=False,
            xaxis_title="Forecast Change (%)",
            yaxis_title="Practice"
        )
        fig_growth.update_yaxes(categoryorder='total ascending')
        
        # Update hover template
        fig_growth.update_traces(
            hovertemplate='<b>%{y}</b><br>' +
                         'Forecast Change: %{x:.1f}%<br>' +
                         'Avg Historical: %{customdata[0]:,.0f}<br>' +
                         'Avg Forecast: %{customdata[1]:,.0f}<br>' +
                         'Absolute Change: %{customdata[2]:+,.0f}<br>' +
                         '<extra></extra>'
        )
        
        st.plotly_chart(fig_growth, use_container_width=True)
        
        # Show summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Highest Appointment Increase", 
                     f"{top30_growth.iloc[0]['GP_NAME'][:30]}...",
                     f"+{top30_growth.iloc[0]['Forecast_Change_Pct']:.1f}%")
        
        with col2:
            practices_growing = (df_growth['Forecast_Change_Pct'] > 0).sum()
            st.metric("Practices Expected More Appointments", 
                     f"{practices_growing} of {len(df_growth)}",
                     f"{practices_growing/len(df_growth)*100:.1f}%")
        
        with col3:
            avg_growth = df_growth['Forecast_Change_Pct'].mean()
            st.metric("Average Growth", f"{avg_growth:+.1f}%")
        
        with col4:
            median_growth = df_growth['Forecast_Change_Pct'].median()
            st.metric("Median Growth", f"{median_growth:+.1f}%")
        
        # Show detailed table
        # st.markdown("#### Detailed Rankings")
        
        # display_df = top30_growth[['GP_NAME', 'ICB_NAME', 'Avg_Historical', 'Avg_Forecast', 
        #                              'Absolute_Change', 'Forecast_Change_Pct']].copy()
        # display_df.columns = ['Practice', 'ICB', 'Avg Historical', 'Avg Forecast', 
        #                       'Change (Appts)', 'Change (%)']
        # display_df['Avg Historical'] = display_df['Avg Historical'].apply(lambda x: f"{x:,.0f}")
        # display_df['Avg Forecast'] = display_df['Avg Forecast'].apply(lambda x: f"{x:,.0f}")
        # display_df['Change (Appts)'] = display_df['Change (Appts)'].apply(lambda x: f"{x:+,.0f}")
        # display_df['Change (%)'] = display_df['Change (%)'].apply(lambda x: f"{x:+.1f}%")
        
        # st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Top 20 Practices by Average FTE Requirements")
        
        # Calculate average FTE per practice
        practice_fte_summary = df_fte.groupby('GP_CODE').agg({
            'Total_FTE_Required': 'mean',
            'GP_FTE_Required': 'mean',
            'Staff_FTE_Required': 'mean'
        }).reset_index()
        
        practice_fte_summary = practice_fte_summary.merge(
            df_metadata[['GP_CODE', 'GP_NAME', 'ICB_NAME']],
            on='GP_CODE',
            how='left'
        )
        
        top20 = practice_fte_summary.nlargest(20, 'Total_FTE_Required')
        
        # Create bar chart
        fig_top20 = px.bar(
            top20,
            y='GP_NAME',
            x='Total_FTE_Required',
            orientation='h',
            title="Top 20 Practices by Average FTE Requirements",
            labels={'Total_FTE_Required': 'Avg Total FTE', 'GP_NAME': 'Practice'},
            color='Total_FTE_Required',
            color_continuous_scale='Blues'
        )
        fig_top20.update_layout(height=600, showlegend=False)
        fig_top20.update_yaxes(categoryorder='total ascending')
        
        st.plotly_chart(fig_top20, use_container_width=True)
    
    with tab3:
        st.subheader("Model Performance Distribution (MAPE)")
        
        # Create MAPE histogram
        fig_mape = px.histogram(
            df_metadata,
            x='Validation_MAPE',
            nbins=50,
            title="Distribution of Model Accuracy (MAPE)",
            labels={'Validation_MAPE': 'MAPE (%)', 'count': 'Number of Practices'},
            color_discrete_sequence=['#1f77b4']
        )
        
        # Add vertical lines for thresholds
        fig_mape.add_shape(
            type="line",
            x0=10, x1=10,
            y0=0, y1=1,
            yref="paper",
            line=dict(color="green", width=2, dash="dash")
        )
        fig_mape.add_annotation(
            x=10, y=1.0, yref="paper",
            text="Excellent (10%)",
            showarrow=False,
            xshift=50,
            yshift=10
        )
        
        fig_mape.add_shape(
            type="line",
            x0=20, x1=20,
            y0=0, y1=1,
            yref="paper",
            line=dict(color="orange", width=2, dash="dash")
        )
        fig_mape.add_annotation(
            x=20, y=1.0, yref="paper",
            text="Good (20%)",
            showarrow=False,
            xshift=50,
            yshift=10
        )
        
        fig_mape.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_mape, use_container_width=True)
        
        # Performance summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            excellent = (df_metadata['Validation_MAPE'] < 10).sum()
            pct_excellent = excellent / len(df_metadata) * 100
            st.metric("Excellent (<10% MAPE)", f"{excellent} ({pct_excellent:.1f}%)")
        
        with col2:
            good = ((df_metadata['Validation_MAPE'] >= 10) & (df_metadata['Validation_MAPE'] < 20)).sum()
            pct_good = good / len(df_metadata) * 100
            st.metric("Good (10-20% MAPE)", f"{good} ({pct_good:.1f}%)")
        
        with col3:
            acceptable = ((df_metadata['Validation_MAPE'] >= 20) & (df_metadata['Validation_MAPE'] < 24)).sum()
            pct_acceptable = acceptable / len(df_metadata) * 100
            st.metric("Acceptable (20-24% MAPE)", f"{acceptable} ({pct_acceptable:.1f}%)")
    
    with tab4:
        st.subheader("Practices by ICB")
        
        # Group by ICB
        icb_summary = df_metadata.groupby('ICB_NAME').agg({
            'GP_CODE': 'count',
            'Validation_MAPE': 'median'
        }).reset_index()
        icb_summary.columns = ['ICB', 'Number of Practices', 'Median MAPE']
        icb_summary = icb_summary.sort_values('Number of Practices', ascending=False)
        
        # Create bar chart
        fig_icb = px.bar(
            icb_summary,
            x='Number of Practices',
            y='ICB',
            orientation='h',
            title="Number of Practices by ICB",
            labels={'Number of Practices': 'Practices', 'ICB': 'Integrated Care Board'},
            color='Median MAPE',
            color_continuous_scale='RdYlGn_r'
        )
        fig_icb.update_layout(height=400)
        fig_icb.update_yaxes(categoryorder='total ascending')
        
        st.plotly_chart(fig_icb, use_container_width=True)
        
        st.dataframe(icb_summary, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### 🔍 General Practice Appointment Forecasting")
    st.markdown("Use the sidebar to select a specific practice for detailed forecasting and resource planning.")
    st.markdown("---")
    
    # ============================================================================
    # SIDEBAR - Practice Selection and Filtering
    # ============================================================================
    st.sidebar.header("🔍 Practice Selection")
    
    # Filter by performance tier
    # performance_tier = st.sidebar.radio(
    #     "Filter by Model Performance:",
    #     ["All Practices", "Excellent (<10% MAPE)", "Good (10-20% MAPE)", "Acceptable (20-24% MAPE)"],
    #     index=0
    # )
    
    # # Apply performance filter
    # if performance_tier == "Excellent (<10% MAPE)":
    #     df_filtered = df_metadata[df_metadata['Validation_MAPE'] < 10].copy()
    # elif performance_tier == "Good (10-20% MAPE)":
    #     df_filtered = df_metadata[(df_metadata['Validation_MAPE'] >= 10) & 
    #                                (df_metadata['Validation_MAPE'] < 20)].copy()
    # elif performance_tier == "Acceptable (20-24% MAPE)":
    #     df_filtered = df_metadata[(df_metadata['Validation_MAPE'] >= 20) & 
    #                                (df_metadata['Validation_MAPE'] < 24)].copy()
    # else:
    #     df_filtered = df_metadata.copy()
    df_filtered = df_metadata.copy()
    
    # Filter by ICB
    icbs = ['All ICBs'] + sorted(df_filtered['ICB_NAME'].unique().tolist())
    selected_icb = st.sidebar.selectbox("Filter by ICB:", icbs)
    
    if selected_icb != 'All ICBs':
        df_filtered = df_filtered[df_filtered['ICB_NAME'] == selected_icb].copy()
    
    # Practice search/selection
    practices_list = df_filtered.sort_values('GP_NAME')
    practice_options = [f"{row['GP_NAME']} ({row['GP_CODE']})" 
                       for _, row in practices_list.iterrows()]
    
    selected_practice_display = st.sidebar.selectbox(
        f"Select Practice ({len(practice_options)} available):",
        practice_options,
        index=0
    )
    
    # Extract GP_CODE from selection
    selected_gp_code = selected_practice_display.split('(')[-1].rstrip(')')
    
    # Get practice info
    practice_info = df_metadata[df_metadata['GP_CODE'] == selected_gp_code].iloc[0]
    
    # Display practice info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Practice:** {practice_info['GP_NAME']}")
    st.sidebar.markdown(f"**Code:** {practice_info['GP_CODE']}")
    st.sidebar.markdown(f"**ICB:** {practice_info['ICB_NAME']}")
    st.sidebar.markdown(f"**Sub-ICB:** {practice_info['SUB_ICB_LOCATION_NAME']}")
    st.sidebar.markdown(f"**Model MAPE:** {practice_info['Validation_MAPE']:.1f}%")
    
    # ============================================================================
    # MAIN CONTENT - Practice Time Series
    # ============================================================================
    st.header(f"📊 {practice_info['GP_NAME']}")
    
    # Get forecast data for selected practice
    practice_forecast = df_forecast[df_forecast['GP_CODE'] == selected_gp_code].copy()
    practice_forecast = practice_forecast.sort_values('Month')
    
    # Merge with FTE data for hover information
    practice_forecast = practice_forecast.merge(
        df_fte[['GP_CODE', 'Month', 'GP_FTE_Required', 'Staff_FTE_Required', 'Total_FTE_Required']],
        on=['GP_CODE', 'Month'],
        how='left'
    )
    
    # Combine historical and validation as "historical" (for training + validation period)
    historical_data = practice_forecast[practice_forecast['Type'].isin(['Historical', 'Validation'])].copy()
    forecast_data = practice_forecast[practice_forecast['Type'] == 'Forecast'].copy()
    
    # Create time series chart
    fig = go.Figure()
    
    # Add historical data (training + validation combined)
    fig.add_trace(go.Scatter(
        x=historical_data['Month'],
        y=historical_data['Total_Appointments'],
        mode='lines+markers',
        name='Historical Data',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=5),
        hovertemplate='<b>%{x|%b %Y}</b><br>Appointments: %{y:,.0f}<extra></extra>'
    ))
    
    # Add forecast data - include last historical point for seamless connection
    if len(historical_data) > 0 and len(forecast_data) > 0:
        # Get the last historical point
        last_hist_date = historical_data['Month'].iloc[-1]
        last_hist_value = historical_data['Total_Appointments'].iloc[-1]
        
        # Prepend to forecast data for continuous line
        forecast_dates = pd.concat([pd.Series([last_hist_date]), forecast_data['Month']]).reset_index(drop=True)
        forecast_values = pd.concat([pd.Series([last_hist_value]), forecast_data['Total_Appointments']]).reset_index(drop=True)
        
        # Prepare customdata for hover with FTE information
        # Create arrays for GP FTE, Staff FTE, Total FTE
        customdata_list = []
        for idx, row in forecast_data.iterrows():
            if pd.notna(row.get('Total_FTE_Required')):
                customdata_list.append([
                    row['GP_FTE_Required'],
                    row['Staff_FTE_Required'],
                    row['Total_FTE_Required']
                ])
            else:
                customdata_list.append([None, None, None])
        
        # Prepend None values for first point (last historical)
        customdata_array = [[None, None, None]] + customdata_list
        
        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=forecast_values,
            mode='lines+markers',
            name='Holt-Winters Forecast',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=6, symbol='diamond'),
            customdata=customdata_array,
            hovertemplate=(
                '<b>%{x|%b %Y}</b><br>' +
                'Forecast: %{y:,.0f} appts<br>' +
                '<b>FTE Required:</b><br>' +
                '  GP: %{customdata[0]:.1f}<br>' +
                '  Staff: %{customdata[1]:.1f}<br>' +
                '  Total: %{customdata[2]:.1f}' +
                '<extra></extra>'
            )
        ))
    else:
        # Fallback if no historical data
        fig.add_trace(go.Scatter(
            x=forecast_data['Month'],
            y=forecast_data['Total_Appointments'],
            mode='lines+markers',
            name='Holt-Winters Forecast',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=6, symbol='diamond'),
            hovertemplate='<b>%{x|%b %Y}</b><br>Forecast: %{y:,.0f}<extra></extra>'
        ))
    
    # Add vertical line to separate historical from forecast
    if len(forecast_data) > 0:
        forecast_start = forecast_data['Month'].min()
        fig.add_shape(
            type="line",
            x0=forecast_start, x1=forecast_start,
            y0=0, y1=1,
            yref="paper",
            line=dict(color="gray", width=2, dash="dot")
        )
        fig.add_annotation(
            x=forecast_start,
            y=1.0,
            yref="paper",
            text="Forecast Start",
            showarrow=False,
            yshift=10
        )
    
    # Update layout
    fig.update_layout(
        title=f"Monthly Appointments - {practice_info['GP_NAME']}",
        xaxis_title="Month",
        yaxis_title="Total Appointments",
        hovermode='x unified',
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ============================================================================
    # METRICS ROW
    # ============================================================================
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_hist = historical_data['Total_Appointments'].mean() if len(historical_data) > 0 else 0
        st.metric("Historical Avg", f"{avg_hist:,.0f}")
    
    with col2:
        avg_forecast = forecast_data['Total_Appointments'].mean() if len(forecast_data) > 0 else 0
        st.metric("Forecast Avg", f"{avg_forecast:,.0f}")
    
    with col3:
        st.metric("Model MAPE", f"{practice_info['Validation_MAPE']:.1f}%")
    
    with col4:
        # Get FTE for this practice
        practice_fte_data = df_fte[df_fte['GP_CODE'] == selected_gp_code]
        avg_fte = practice_fte_data['Total_FTE_Required'].mean() if len(practice_fte_data) > 0 else 0
        st.metric("Avg FTE Needed", f"{avg_fte:.1f}")
    
    with col5:
        if avg_hist > 0 and avg_forecast > 0:
            pct_change = ((avg_forecast / avg_hist) - 1) * 100
            st.metric("Forecast Change", f"{pct_change:+.1f}%")
        else:
            st.metric("Forecast Change", "N/A")
    
    # ============================================================================
    # FTE REQUIREMENTS SECTION
    # ============================================================================
    st.markdown("---")
    st.header("👥 Resource Requirements (FTE)")
    
    if len(practice_fte_data) > 0:
        # Create FTE breakdown chart
        fig_fte = go.Figure()
        
        fig_fte.add_trace(go.Bar(
            x=practice_fte_data['Month'],
            y=practice_fte_data['GP_FTE_Required'],
            name='GP FTE',
            marker_color='#1f77b4',
            hovertemplate='<b>%{x|%b %Y}</b><br>GP FTE: %{y:.1f}<extra></extra>'
        ))
        
        fig_fte.add_trace(go.Bar(
            x=practice_fte_data['Month'],
            y=practice_fte_data['Staff_FTE_Required'],
            name='Staff FTE',
            marker_color='#ff7f0e',
            hovertemplate='<b>%{x|%b %Y}</b><br>Staff FTE: %{y:.1f}<extra></extra>'
        ))
        
        fig_fte.update_layout(
            title="Monthly FTE Requirements (Feb 2026 - Jan 2027)",
            xaxis_title="Month",
            yaxis_title="FTE Required",
            barmode='stack',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_fte, use_container_width=True)
        
        # FTE summary table
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_gp_fte = practice_fte_data['GP_FTE_Required'].mean()
            st.metric("Avg GP FTE", f"{avg_gp_fte:.1f}")
        
        with col2:
            avg_staff_fte = practice_fte_data['Staff_FTE_Required'].mean()
            st.metric("Avg Staff FTE", f"{avg_staff_fte:.1f}")
        
        with col3:
            total_avg_fte = practice_fte_data['Total_FTE_Required'].mean()
            st.metric("Total Avg FTE", f"{total_avg_fte:.1f}")
    
    # ============================================================================
    # DATA TABLES
    # ============================================================================
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📋 Forecast Data", "👥 FTE Requirements"])
    
    with tab1:
        st.subheader("Forecast Details")
        forecast_display = forecast_data[['Month', 'Total_Appointments']].copy()
        forecast_display['Month'] = forecast_display['Month'].dt.strftime('%B %Y')
        forecast_display.columns = ['Month', 'Forecasted Appointments']
        forecast_display['Forecasted Appointments'] = forecast_display['Forecasted Appointments'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(forecast_display, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Monthly FTE Requirements")
        if len(practice_fte_data) > 0:
            fte_display = practice_fte_data[['Month', 'GP_FTE_Required', 'Staff_FTE_Required', 'Total_FTE_Required']].copy()
            fte_display['Month'] = fte_display['Month'].dt.strftime('%B %Y')
            fte_display.columns = ['Month', 'GP FTE', 'Staff FTE', 'Total FTE']
            fte_display['GP FTE'] = fte_display['GP FTE'].apply(lambda x: f"{x:.1f}")
            fte_display['Staff FTE'] = fte_display['Staff FTE'].apply(lambda x: f"{x:.1f}")
            fte_display['Total FTE'] = fte_display['Total FTE'].apply(lambda x: f"{x:.1f}")
            st.dataframe(fte_display, use_container_width=True, hide_index=True)

except FileNotFoundError as e:
    st.error(f"""
    ⚠️ **Practice data files not found!**
    
    Please ensure the following files exist in the `./outputs/` directory:
    - `practice_sarima_validation_successful.csv` (validation results)
    - `london_gp_lookup.csv` (practice lookup data)
    - `practice_forecast_total.csv` (forecast data)
    - `practice_fte_requirements.csv` (FTE requirements)
    
    Error: {str(e)}
    """)
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.exception(e)
