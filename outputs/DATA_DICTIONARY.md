
# NHS GP Appointments Forecast - Data Dictionary

## Forecast Files

### forecast_production.csv
- **Description**: Production forecasts at Sub-ICB level (Feb 2026 - Jan 2027)
- **Rows**: 1,272 (106 Sub-ICBs × 12 months)
- **Columns**: SUB_ICB_CODE, SUB_ICB_NAME, ICB_CODE, REGION_CODE, Month, Forecast_Appointments

### forecast_icb.csv
- **Description**: Aggregated forecasts at ICB level
- **Rows**: 504 (42 ICBs × 12 months)
- **Columns**: ICB_CODE, Month, Forecast_Appointments, Num_Sub_ICBs

### forecast_regional.csv
- **Description**: Aggregated forecasts at Regional level
- **Rows**: 84 (7 regions × 12 months)
- **Columns**: REGION_CODE, Month, Forecast_Appointments, Num_Sub_ICBs, Num_ICBs

## FTE Requirement Files

### fte_gp.csv
- **Description**: GP FTE requirements at Sub-ICB level
- **Capacity**: 25 appts/day @ 100% utilization = 525 appts/month per FTE
- **Rows**: 1,272 (106 Sub-ICBs × 12 months)
- **Columns**: All forecast columns + GP_Appointments, Required_GP_FTE

### fte_staff.csv
- **Description**: Practice Staff FTE requirements at Sub-ICB level
- **Capacity**: 30 appts/day @ 100% utilization = 630 appts/month per FTE
- **Rows**: 1,272 (106 Sub-ICBs × 12 months)
- **Columns**: All forecast columns + Staff_Appointments, Required_Staff_FTE

### fte_icb_gp.csv
- **Description**: GP FTE requirements aggregated to ICB level
- **Rows**: 504 (42 ICBs × 12 months)
- **Columns**: ICB_CODE, Month, GP_Appointments, Required_GP_FTE, Num_Sub_ICBs

### fte_regional_gp.csv
- **Description**: GP FTE requirements aggregated to Regional level
- **Rows**: 84 (7 regions × 12 months)
- **Columns**: REGION_CODE, Month, GP_Appointments, Required_GP_FTE, Num_Sub_ICBs

### resource_analysis_combined.csv
- **Description**: Combined GP + Practice Staff FTE by Sub-ICB
- **Rows**: 1,272 (106 Sub-ICBs × 12 months)
- **Columns**: All forecast columns + Required_GP_FTE, Required_Staff_FTE, Total_FTE

## Priority and Analysis Files

### priority_locations.csv
- **Description**: Resource priority rankings for all Sub-ICBs
- **Rows**: 106 Sub-ICBs
- **Columns**: SUB_ICB_CODE, SUB_ICB_NAME, ICB_CODE, REGION_CODE, REGION_NAME,
              Avg_Total_FTE, Seasonal_Swing, Priority_Score, Priority_Flag
- **Priority Flags**: CRITICAL (High Demand + High Seasonality), HIGH (one flag), STANDARD (no flags)

## Summary Tables

### summary_executive.csv
- **Description**: Executive summary with 20 key metrics
- **Content**: National totals, averages, peaks, capacity assumptions

### summary_regional.csv
- **Description**: Regional-level summary statistics
- **Rows**: 7 regions
- **Columns**: Region, Avg_GP_FTE, Avg_Staff_FTE, Total_FTE, Num_Sub_ICBs, Num_ICBs, 
              Pct_of_National, FTE_per_Sub_ICB

### summary_top20_sub_icbs.csv
- **Description**: Top 20 Sub-ICBs by FTE requirement
- **Rows**: 20
- **Columns**: SUB_ICB_CODE, SUB_ICB_NAME, REGION_CODE, Required_GP_FTE, Required_Staff_FTE,
              Total_FTE, Priority_Flag, Priority_Score

### summary_capacity_assumptions.csv
- **Description**: Documentation of all capacity parameters
- **Content**: GP capacity, Practice Staff capacity, historical proportions, model settings

## Historical Data

### historical_monthly_sub_icb.csv
- **Description**: Full 30-month historical data (Aug 2023 - Jan 2026)
- **Rows**: 3,180 (106 Sub-ICBs × 30 months)
- **Columns**: SUB_ICB_CODE, SUB_ICB_NAME, ICB_CODE, REGION_CODE, APPT_MONTH, COUNT_OF_APPOINTMENTS

## Model Information

- **Forecasting Model**: Holt-Winters (Exponential Smoothing)
- **Seasonal Period**: 12 months
- **Seasonality Types**: 90 Additive, 16 Multiplicative (auto-selected per Sub-ICB by AIC)
- **Training Period**: Aug 2023 - Jul 2025 (24 months)
- **Validation Period**: Aug 2025 - Jan 2026 (6 months)
- **Forecast Period**: Feb 2026 - Jan 2027 (12 months)

## Generated
This dataset was generated on: 2026-03-15 15:13:36

## Contact
For questions about this forecast, refer to the forecasting.ipynb notebook.
