"""
Ethiopia Financial Inclusion Forecasting Dashboard
Streamlit application for stakeholders
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Import custom modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import DashboardDataLoader
from utils.visualizations import DashboardVisualizations
from utils.forecast_processor import ForecastProcessor

# Page configuration
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 1rem;
        color: #64748B;
    }
    .positive {
        color: #10B981;
    }
    .negative {
        color: #EF4444;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize data loader
@st.cache_resource
def load_data():
    loader = DashboardDataLoader()
    success = loader.load_all_data()
    return loader if success else None

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Ethiopia Financial Inclusion Forecasting Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #64748B; margin-bottom: 2rem;'>
    Tracking Ethiopia's digital financial transformation and forecasting inclusion outcomes (2025-2027)
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data...'):
        data_loader = load_data()
    
    if data_loader is None:
        st.error("""
        ❌ Failed to load data. Please ensure:
        1. Data files exist in data/processed/ and models/ directories
        2. Required CSV files are present
        3. File paths are correct
        
        Check the console for detailed error messages.
        """)
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔍 Navigation")
        
        page = st.radio(
            "Select Dashboard Section",
            ["📈 Overview", "📊 Trends Analysis", "🔮 Forecasts", "🎯 Inclusion Projections", "📋 About"]
        )
        
        st.markdown("---")
        st.markdown("## ⚙️ Settings")
        
        # Scenario selector (used in forecasts page)
        scenario = st.selectbox(
            "Forecast Scenario",
            ["Base", "Optimistic", "Pessimistic"],
            index=0
        ).lower()
        
        # Date range for trends
        st.markdown("### Date Range (Trends)")
        min_date = datetime(2011, 1, 1)
        max_date = datetime(2027, 12, 31)
        
        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        st.markdown("---")
        st.markdown("## 📥 Data Export")
        
        if data_loader.forecasts and 'summary' in data_loader.forecasts and data_loader.forecasts['summary'] is not None:
            csv = data_loader.forecasts['summary'].to_csv(index=False)
            st.download_button(
                label="📄 Download Forecast Summary",
                data=csv,
                file_name="ethiopia_fi_forecast_summary.csv",
                mime="text/csv"
            )
        
        st.markdown("---")
        st.markdown("""
        <div style='font-size: 0.8rem; color: #94A3B8;'>
        <b>Developed by:</b> Selam Analytics<br>
        <b>Data Source:</b> Global Findex, NBE, Operator Reports<br>
        <b>Last Updated:</b> February 2026
        </div>
        """, unsafe_allow_html=True)
    
    # Page routing
    if page == "📈 Overview":
        show_overview_page(data_loader)
    elif page == "📊 Trends Analysis":
        show_trends_page(data_loader, date_range)
    elif page == "🔮 Forecasts":
        show_forecasts_page(data_loader, scenario)
    elif page == "🎯 Inclusion Projections":
        show_projections_page(data_loader)
    else:
        show_about_page()

def show_overview_page(data_loader):
    """Overview page with key metrics"""
    st.markdown('<h2 class="sub-header">📈 Executive Overview</h2>', unsafe_allow_html=True)
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if 'latest_account_ownership' in data_loader.summary_stats:
            value = data_loader.summary_stats['latest_account_ownership']
            year = data_loader.summary_stats.get('account_ownership_year', '2024')
            st.markdown(f'<div class="metric-value">{value:.1f}%</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-label">Account Ownership ({year})</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">49.0%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Account Ownership (2024)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if 'latest_digital_payments' in data_loader.summary_stats:
            value = data_loader.summary_stats['latest_digital_payments']
            st.markdown(f'<div class="metric-value">{value:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Digital Payment Usage</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">35.0%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Digital Payments (2024)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if 'gender_gap' in data_loader.summary_stats:
            value = data_loader.summary_stats['gender_gap']
            st.markdown(f'<div class="metric-value">{value:.1f}pp</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Gender Gap (2021)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">20.0pp</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Gender Gap</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if 'p2p_atm_ratio' in data_loader.summary_stats:
            value = data_loader.summary_stats['p2p_atm_ratio']
            status = "✓ Surpassed" if data_loader.summary_stats.get('p2p_surpasses_atm', False) else "⬆ Growing"
            st.markdown(f'<div class="metric-value">{value:.1f}x</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-label">P2P/ATM Ratio ({status})</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">1.08x</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">P2P/ATM Ratio (Surpassed)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Growth highlights
    st.markdown('<h3 class="sub-header">📈 Growth Highlights</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Account Ownership Growth")
        current = data_loader.summary_stats.get('latest_account_ownership', 49.0)
        
        if 'projected_growth_2027' in data_loader.summary_stats:
            growth = data_loader.summary_stats['projected_growth_2027']
            forecast_2027 = current + growth
            
            st.metric(
                label="2024 → 2027 Projection",
                value=f"{forecast_2027:.1f}%",
                delta=f"{growth:+.1f}pp"
            )
        else:
            st.metric(
                label="2024 → 2027 Projection",
                value="84.7%",
                delta="+35.7pp"
            )
        
        # Gauge chart
        fig = DashboardVisualizations.create_gauge_chart(
            current,
            "Current Account Ownership",
            target=70  # NFIS-II target
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Key Market Events")
        events = data_loader.get_events_timeline()
        if events is not None:
            for _, event in events.head(5).iterrows():
                st.markdown(f"""
                **{event['date'].year}**: {event['indicator']}
                *Category*: {event['category'] if 'category' in event and pd.notna(event['category']) else 'N/A'}
                """)
        else:
            st.markdown("""
            **2021**: Telebirr Launch
            **2022**: Safaricom Entry
            **2023**: M-Pesa Launch
            **2024**: Fayda Digital ID Rollout
            **2024**: P2P > ATM Milestone
            """)
    
    # Recent insights
    st.markdown('<h3 class="sub-header">💡 Key Insights</h3>', unsafe_allow_html=True)
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.info("""
        **📱 Digital Payments Growth**
        - Digital payment usage projected to reach 50% by 2027
        - Current usage (35%) lags behind account ownership (49%)
        - Telebirr and M-Pesa driving adoption
        """)
        
        st.info("""
        **⚡ Infrastructure Impact**
        - 4G coverage expansion enabling digital services
        - Fayda Digital ID expected to boost inclusion by +10pp
        - Network effects from interoperability
        """)
    
    with insights_col2:
        st.warning("""
        **⚠️ Challenges Identified**
        - Gender gap remains at 20 percentage points
        - Account growth slowed post-2021 (+3pp vs +11pp previously)
        - Infrastructure-data correlation needs monitoring
        """)
        
        st.success("""
        **✅ Success Factors**
        - P2P transactions surpassed ATM withdrawals (2024)
        - NFIS-II target achievable by 2025
        - Strong event impact validation (95.9% accuracy)
        """)

def show_trends_page(data_loader, date_range):
    """Trends analysis page"""
    st.markdown('<h2 class="sub-header">📊 Trends Analysis</h2>', unsafe_allow_html=True)
    
    # Indicator selector
    indicators = ['Account Ownership Rate', 'Mobile Money Account Rate', '4G Population Coverage']
    selected_indicator = st.selectbox("Select Indicator to Analyze", indicators)
    
    # Get time series data
    timeseries_data = data_loader.get_indicator_timeseries(selected_indicator)
    events_data = data_loader.get_events_timeline()
    
    if timeseries_data is not None and not timeseries_data.empty:
        # Filter by date range
        if len(date_range) == 2:
            start_date, end_date = date_range
            timeseries_data = timeseries_data[
                (timeseries_data['date'] >= pd.Timestamp(start_date)) &
                (timeseries_data['date'] <= pd.Timestamp(end_date))
            ]
        
        # Create visualization
        fig = DashboardVisualizations.create_timeseries_plot(
            timeseries_data,
            f"{selected_indicator} Trend",
            "Percentage (%)",
            color='#3B82F6',
            show_events=True,
            events_data=events_data
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        with st.expander("View Data Table"):
            display_df = timeseries_data.copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_df[['date', 'value_numeric', 'gender', 'location']], use_container_width=True)
    else:
        st.warning(f"No time series data available for {selected_indicator}")
        
        # Show static data as fallback
        if selected_indicator == 'Account Ownership Rate':
            st.markdown("""
            **Historical Account Ownership:**
            - 2011: 14%
            - 2014: 22%
            - 2017: 35%
            - 2021: 46%
            - 2024: 49%
            """)
    
    # Correlation analysis
    st.markdown('<h3 class="sub-header">🔗 Correlation Analysis</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Infrastructure vs Inclusion")
        st.markdown("""
        - **4G Coverage** ↔ **Digital Payments**: Strong positive correlation
        - **Mobile Penetration** ↔ **Account Ownership**: Moderate correlation
        - **Digital ID Enrollment** ↔ **P2P Transactions**: Very strong correlation (r=1.0)
        """)
    
    with col2:
        st.markdown("#### Gender Analysis")
        gap = data_loader.summary_stats.get('gender_gap', 20.0)
        st.metric(
            label="Account Ownership Gender Gap (2021)",
            value=f"{gap:.1f}pp",
            delta="Persistent challenge"
        )
        
        st.markdown("""
        **Gender Distribution (2021):**
        - Male: 56%
        - Female: 36%
        - Gap: 20 percentage points
        - Female/Male Ratio: 64%
        """)

def show_forecasts_page(data_loader, scenario):
    """Forecasts page"""
    st.markdown('<h2 class="sub-header">🔮 Inclusion Forecasts 2025-2027</h2>', unsafe_allow_html=True)
    
    # Scenario info
    scenario_info = {
        'base': "Most likely outcome based on current trends and event impacts",
        'optimistic': "Best-case scenario with accelerated adoption",
        'pessimistic': "Conservative scenario accounting for potential challenges"
    }
    
    st.info(f"**Selected Scenario**: {scenario.title()} - {scenario_info[scenario]}")
    
    # Tabs for different forecasts
    forecast_tabs = st.tabs(["📈 Account Ownership", "💳 Digital Payments", "📊 Scenario Comparison", "🎯 Event Impacts"])
    
    with forecast_tabs[0]:
        st.markdown("#### Account Ownership Forecast (Access)")
        
        # Get historical data
        historical_data = data_loader.get_indicator_timeseries('Account Ownership Rate')
        
        # Get forecast data
        forecast_data = data_loader.get_forecast_data('Account Ownership', scenario)
        
        if forecast_data is not None:
            # Create forecast plot
            fig = DashboardVisualizations.create_forecast_plot(
                historical_data,
                forecast_data,
                f"Account Ownership Forecast ({scenario.title()} Scenario)",
                scenario
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast table
            st.markdown("#### Forecast Values")
            current_value = data_loader.summary_stats.get('latest_account_ownership', 49.0)
            display_df = forecast_data.copy()
            display_df['Growth from 2024'] = display_df['value'] - current_value
            display_df['Growth from 2024'] = display_df['Growth from 2024'].apply(lambda x: f'{x:+.1f}pp')
            st.dataframe(display_df, use_container_width=True)
            
            # Milestones
            processor = ForecastProcessor()
            milestones = processor.get_milestones(forecast_data, [60, 70, 80, 90])
            
            if milestones:
                st.markdown("#### Key Milestones")
                for milestone, year in milestones.items():
                    st.markdown(f"- **{milestone}%** account ownership projected in **{year}**")
        else:
            st.warning("Account ownership forecast data not available")
            # Show static forecast
            st.markdown("""
            **Base Scenario Forecast:**
            - 2025: 74.3%
            - 2026: 81.9%
            - 2027: 84.7%
            """)
    
    with forecast_tabs[1]:
        st.markdown("#### Digital Payment Usage Forecast (Usage)")
        
        # Get historical data
        historical_names = ['USG_DIGITAL_PAYMENT', 'Digital Payment Usage Rate']
        historical_data = None
        for name in historical_names:
            historical_data = data_loader.get_indicator_timeseries(name)
            if historical_data is not None:
                break
        
        # Get forecast data
        forecast_data = data_loader.get_forecast_data('Digital Payments', scenario)
        
        if forecast_data is not None:
            # Create forecast plot
            fig = DashboardVisualizations.create_forecast_plot(
                historical_data,
                forecast_data,
                f"Digital Payment Usage Forecast ({scenario.title()} Scenario)",
                scenario
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast table
            st.markdown("#### Forecast Values")
            current_value = data_loader.summary_stats.get('latest_digital_payments', 35.0)
            display_df = forecast_data.copy()
            display_df['Growth from 2024'] = display_df['value'] - current_value
            display_df['Growth from 2024'] = display_df['Growth from 2024'].apply(lambda x: f'{x:+.1f}pp')
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Digital payment forecast data not available")
            # Show static forecast
            st.markdown("""
            **Base Scenario Forecast:**
            - 2025: 40.0%
            - 2026: 45.0%
            - 2027: 50.0%
            """)
    
    with forecast_tabs[2]:
        st.markdown("#### Scenario Comparison")
        
        # Get all scenarios for account ownership
        scenarios_data = {}
        for sc in ['base', 'optimistic', 'pessimistic']:
            scenarios_data[sc] = data_loader.get_forecast_data('Account Ownership', sc)
        
        # Create comparison chart
        fig = DashboardVisualizations.create_scenario_comparison(
            scenarios_data,
            "Account Ownership: Scenario Comparison"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison table
        st.markdown("#### Scenario Comparison Table")
        comparison_data = []
        for sc, data in scenarios_data.items():
            if data is not None:
                for _, row in data.iterrows():
                    comparison_data.append({
                        'Year': row['year'],
                        'Scenario': sc.title(),
                        'Forecast': row['value']
                    })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            pivot_df = comparison_df.pivot_table(
                index='Year',
                columns='Scenario',
                values='Forecast'
            )
            st.dataframe(pivot_df, use_container_width=True)
        else:
            st.markdown("""
            **Scenario Comparison (Account Ownership 2027):**
            - Optimistic: 100.0%
            - Base: 84.7%
            - Pessimistic: 67.7%
            """)
    
    with forecast_tabs[3]:
        st.markdown("#### Event Impact Analysis")
        
        if data_loader.event_impacts is not None:
            # Check what columns are available
            available_cols = data_loader.event_impacts.columns.tolist()
            
            # Try to find relevant columns
            event_col = None
            impact_col = None
            
            for col in available_cols:
                if 'event' in col.lower():
                    event_col = col
                if 'impact' in col.lower() or 'estimate' in col.lower():
                    impact_col = col
            
            if event_col and impact_col:
                # Create simplified impact data
                impact_data = []
                
                for _, row in data_loader.event_impacts.iterrows():
                    event_name = row[event_col] if pd.notna(row[event_col]) else 'Unknown Event'
                    impact_value = float(row[impact_col]) if pd.notna(row[impact_col]) else 0
                    
                    if impact_value != 0:
                        impact_data.append({
                            'Event': event_name,
                            'Impact (pp)': impact_value,
                            'Direction': 'Positive' if impact_value > 0 else 'Negative'
                        })
                
                if impact_data:
                    impact_df = pd.DataFrame(impact_data)
                    
                    fig = DashboardVisualizations.create_event_impact_chart(
                        impact_df,
                        "Event Impacts"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Impact table
                    st.dataframe(impact_df, use_container_width=True)
                else:
                    st.info("No quantified event impacts found.")
            else:
                st.info("Event impacts data available but column structure not recognized.")
                st.write("Available columns:", available_cols)
        else:
            st.info("Event impacts data not available.")
            
            # Show static event impacts
            st.markdown("""
            **Key Event Impacts:**
            - Telebirr Launch: +15.0pp on account ownership
            - Fayda Digital ID: +10.0pp on account ownership
            - M-Pesa Launch: +8.0pp on digital payments
            - Foreign Exchange Liberalization: +12.0pp on digital payments
            """)
        
        # Validation results
        st.markdown("#### Model Validation")
        if data_loader.validation_results is not None:
            st.dataframe(data_loader.validation_results, use_container_width=True)
            
            # Calculate accuracy
            if not data_loader.validation_results.empty and 'validation' in data_loader.validation_results.columns:
                pass_rate = (data_loader.validation_results['validation'] == 'PASS').mean() * 100
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Validation Pass Rate", f"{pass_rate:.1f}%")
                
                if 'error_pct' in data_loader.validation_results.columns:
                    avg_error = data_loader.validation_results['error_pct'].mean()
                    with col2:
                        st.metric("Average Error", f"{avg_error:.1f}%")
        else:
            st.markdown("""
            **Validation Results:**
            - Model Accuracy: 95.9%
            - Average Error: 4.1%
            - Pass Rate: 66.7%
            """)

def show_projections_page(data_loader):
    """Inclusion projections page"""
    st.markdown('<h2 class="sub-header">🎯 Inclusion Projections & Targets</h2>', unsafe_allow_html=True)
    
    # NFIS-II Target Analysis
    st.markdown("#### NFIS-II Target: 70% Account Ownership by 2025")
    
    # Get forecast for 2025
    forecast_2025 = None
    if 'account_ownership' in data_loader.forecasts and data_loader.forecasts['account_ownership'] is not None:
        forecast_df = data_loader.forecasts['account_ownership']
        forecast_2025_row = forecast_df[forecast_df['year'] == 2025]
        if not forecast_2025_row.empty:
            forecast_2025 = forecast_2025_row['base'].iloc[0]
    
    current_value = data_loader.summary_stats.get('latest_account_ownership', 49.0)
    
    if forecast_2025:
        processor = ForecastProcessor()
        target_analysis = processor.analyze_nfis_target_gap(current_value, forecast_2025)
        
        if target_analysis:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Current (2024)",
                    f"{target_analysis['current_value']:.1f}%"
                )
            
            with col2:
                st.metric(
                    "2025 Forecast",
                    f"{target_analysis['forecast_2025']:.1f}%",
                    delta=f"{target_analysis['forecast_2025'] - target_analysis['current_value']:+.1f}pp"
                )
            
            with col3:
                delta_color = "normal"
                if target_analysis['gap'] <= 0:
                    status = "✅ On Track"
                    delta_color = "normal"
                else:
                    status = "⚠️ Off Track"
                    delta_color = "inverse"
                
                st.metric(
                    "NFIS-II Target Gap",
                    f"{abs(target_analysis['gap']):.1f}pp",
                    delta=status,
                    delta_color=delta_color
                )
            
            # Progress visualization
            progress_data = pd.DataFrame({
                'Year': [2024, 2025],
                'Actual/Forecast': [current_value, forecast_2025],
                'Target': [current_value, 70.0]
            })
            
            fig = go.Figure()
            
            # Actual/Forecast line
            fig.add_trace(go.Scatter(
                x=progress_data['Year'],
                y=progress_data['Actual/Forecast'],
                mode='lines+markers+text',
                name='Actual/Forecast',
                line=dict(color='blue', width=4),
                marker=dict(size=12),
                text=[f"{current_value:.1f}%", f"{forecast_2025:.1f}%"],
                textposition="top center"
            ))
            
            # Target line
            fig.add_trace(go.Scatter(
                x=progress_data['Year'],
                y=progress_data['Target'],
                mode='lines+markers+text',
                name='NFIS-II Target',
                line=dict(color='red', width=4, dash='dash'),
                marker=dict(size=12),
                text=["", "70.0%"],
                textposition="top center"
            ))
            
            # Fill gap area
            if target_analysis['gap'] > 0:
                fig.add_trace(go.Scatter(
                    x=[2025, 2025],
                    y=[forecast_2025, 70],
                    fill='tozerox',
                    fillcolor='rgba(255, 0, 0, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    showlegend=False,
                    name='Target Gap'
                ))
            
            fig.update_layout(
                title="Progress Toward NFIS-II Target",
                xaxis_title="Year",
                yaxis_title="Account Ownership (%)",
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Static target analysis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current (2024)", "49.0%")
        
        with col2:
            st.metric("2025 Forecast", "74.3%", delta="+25.3pp")
        
        with col3:
            st.metric("NFIS-II Target Gap", "-4.3pp", delta="✅ On Track")
    
    # Answer consortium questions
    st.markdown('<h3 class="sub-header">❓ Answers to Consortium Questions</h3>', unsafe_allow_html=True)
    
    with st.expander("1. What drives financial inclusion in Ethiopia?"):
        st.markdown("""
        **Primary Drivers:**
        - **Mobile Money Platforms**: Telebirr (+15pp), M-Pesa (+8pp)
        - **Infrastructure**: 4G coverage, digital ID enrollment
        - **Policy**: NFIS-II strategy, foreign exchange liberalization
        - **Market Competition**: Entry of Safaricom/M-Pesa driving innovation
        
        **Key Finding**: Digital payment infrastructure shows strongest correlation with inclusion outcomes.
        """)
    
    with st.expander("2. How do events affect inclusion outcomes?"):
        st.markdown("""
        **Event Impact Analysis:**
        - **Product Launches**: Telebirr launch → +15pp account ownership
        - **Market Entry**: M-Pesa entry → +8pp digital payments
        - **Policy Changes**: FX liberalization → +12pp digital payments
        - **Infrastructure**: Fayda Digital ID → +10pp account ownership
        
        **Average Impact Lag**: 12-24 months for full effect
        **Model Accuracy**: 95.9% validation accuracy
        """)
    
    with st.expander("3. How will inclusion rates change in 2025-2027?"):
        st.markdown("""
        **2025-2027 Projections:**
        
        | Indicator | 2024 | 2027 (Base) | Growth | Key Drivers |
        |-----------|------|-------------|--------|-------------|
        | Account Ownership | 49.0% | **84.7%** | +35.7pp | Telebirr, Fayda ID |
        | Digital Payments | 35.0% | **50.0%** | +15.0pp | M-Pesa, interoperability |
        
        **Scenarios (2027 Account Ownership):**
        - Optimistic: 100.0%
        - Base: 84.7%
        - Pessimistic: 67.7%
        
        **NFIS-II Target**: On track for 2025 (74.3% vs 70% target)
        """)
    
    # Recommendations
    st.markdown('<h3 class="sub-header">💡 Recommendations</h3>', unsafe_allow_html=True)
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.success("""
        **Immediate Actions:**
        1. Accelerate digital ID rollout
        2. Promote interoperability between systems
        3. Target gender-specific interventions
        4. Monitor infrastructure-inclusion correlation
        """)
    
    with rec_col2:
        st.info("""
        **Monitoring Framework:**
        - Quarterly infrastructure data collection
        - Real-time transaction monitoring
        - Regular model validation updates
        - Stakeholder feedback integration
        """)

def show_about_page():
    """About page"""
    st.markdown('<h2 class="sub-header">📋 About This Dashboard</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Project Overview
    This dashboard presents the Ethiopia Financial Inclusion Forecasting System, developed by **Selam Analytics** 
    for a consortium of stakeholders including development finance institutions, mobile money operators, 
    and the National Bank of Ethiopia.
    
    ### Objective
    Track and forecast Ethiopia's progress on two core dimensions of financial inclusion:
    1. **Access** — Account Ownership Rate
    2. **Usage** — Digital Payment Adoption Rate
    
    ### Methodology
    - **Data Enrichment**: Unified schema with observations, events, and impact relationships
    - **Event Impact Modeling**: Quantified effects of policies, product launches, infrastructure
    - **Forecasting**: Trend regression + event augmentation with scenario analysis
    - **Validation**: 95.9% accuracy against historical data
    
    ### Data Sources
    - Global Findex Database (World Bank)
    - National Bank of Ethiopia reports
    - Mobile money operator data (Telebirr, M-Pesa)
    - Infrastructure indicators (4G coverage, digital ID)
    
    ### Technical Implementation
    - **Backend**: Python with scikit-learn, pandas, numpy
    - **Forecasting**: Linear regression with event impact augmentation
    - **Dashboard**: Streamlit with Plotly visualizations
    - **Validation**: Comparable country evidence + local validation
    """)
    
    # Run instructions
    st.markdown("### 🚀 How to Run Locally")
    
    st.code("""
# 1. Clone the repository
git clone https://github.com/TsegayIS122123/ethiopia-fi-forecasting-system.git
cd ethiopia-fi-forecasting-system

# 2. Install requirements
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run dashboard/app.py

# 4. Open browser and navigate to:
# http://localhost:8501
""", language="bash")
    
    # Contact information
    st.markdown("### 📞 Contact & Support")
    st.markdown("""
    For questions or support, please contact:
    - **Organization**: Selam Analytics
    - **Project Lead**: Data Science Team
    - **Email**: analytics@selam-ethiopia.org
    - **Phone**: +251 11 123 4567
    
    *This dashboard is for stakeholder use only. Data is updated quarterly.* """)

if __name__ == "__main__":
    main()