"""
Visualization utilities for the dashboard
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

class DashboardVisualizations:
    """Creates interactive visualizations for the dashboard"""
    
    @staticmethod
    def create_timeseries_plot(data, title, yaxis_title, color='blue', show_events=False, events_data=None):
        """Create interactive time series plot - SIMPLIFIED VERSION"""
        fig = go.Figure()
        
        # Add main time series
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['value_numeric'],
            mode='lines+markers',
            name=title,
            line=dict(color=color, width=3),
            marker=dict(size=8),
            hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.1f}%<extra></extra>'
        ))
        
        # Add gender breakdown if available
        if 'gender' in data.columns and data['gender'].nunique() > 1:
            for gender in data['gender'].unique():
                gender_data = data[data['gender'] == gender]
                if not gender_data.empty:
                    fig.add_trace(go.Scatter(
                        x=gender_data['date'],
                        y=gender_data['value_numeric'],
                        mode='lines+markers',
                        name=f'{gender.title()}',
                        line=dict(dash='dash', width=2),
                        hovertemplate='Gender: ' + gender + '<br>Date: %{x|%Y-%m-%d}<br>Value: %{y:.1f}%<extra></extra>'
                    ))
        
        # Add events if requested - SIMPLIFIED APPROACH
        if show_events and events_data is not None:
            # Ensure we have valid datetime
            events_data = events_data.copy()
            if 'date' in events_data.columns:
                events_data['date'] = pd.to_datetime(events_data['date'], errors='coerce')
                events_data = events_data.dropna(subset=['date'])
                
                # Create a separate trace for events
                event_texts = []
                for _, event in events_data.iterrows():
                    event_name = str(event.get('indicator', 'Event'))[:20]
                    event_date = event['date']
                    if pd.notna(event_date):
                        event_texts.append(f"{event_date.strftime('%Y-%m')}: {event_name}")
                
                # Add events as a separate trace with markers
                fig.add_trace(go.Scatter(
                    x=events_data['date'],
                    y=[data['value_numeric'].max() * 0.9] * len(events_data),
                    mode='markers',
                    name='Events',
                    marker=dict(
                        symbol='triangle-down',
                        size=12,
                        color='red',
                        line=dict(width=2, color='darkred')
                    ),
                    text=event_texts,
                    hovertemplate='%{text}<extra></extra>',
                    showlegend=True
                ))
        
        # Update layout
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            xaxis_title="Date",
            yaxis_title=yaxis_title,
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def create_forecast_plot(historical_data, forecast_data, title, scenario='base'):
        """Create forecast visualization with historical data"""
        fig = go.Figure()
        
        # Historical data
        if historical_data is not None:
            fig.add_trace(go.Scatter(
                x=historical_data['date'],
                y=historical_data['value_numeric'],
                mode='lines+markers',
                name='Historical',
                line=dict(color='black', width=3),
                marker=dict(size=8),
                hovertemplate='Date: %{x|%Y}<br>Value: %{y:.1f}%<extra></extra>'
            ))
        
        # Forecast data
        if forecast_data is not None:
            forecast_years = pd.to_datetime(forecast_data['year'], format='%Y')
            
            # Main forecast line
            fig.add_trace(go.Scatter(
                x=forecast_years,
                y=forecast_data['value'],
                mode='lines+markers',
                name=f'Forecast ({scenario})',
                line=dict(color='blue', width=3, dash='dash'),
                marker=dict(size=10),
                hovertemplate='Year: %{x|%Y}<br>Forecast: %{y:.1f}%<extra></extra>'
            ))
            
            # Confidence interval if available
            if 'lower' in forecast_data.columns and 'upper' in forecast_data.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_years.tolist() + forecast_years.tolist()[::-1],
                    y=forecast_data['upper'].tolist() + forecast_data['lower'].tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(0, 100, 255, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo='skip',
                    showlegend=True,
                    name='95% Confidence Interval'
                ))
        
        # Update layout
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            xaxis_title="Year",
            yaxis_title="Percentage (%)",
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def create_scenario_comparison(forecasts_dict, title):
        """Compare multiple forecast scenarios"""
        fig = go.Figure()
        
        colors = {'base': 'blue', 'optimistic': 'green', 'pessimistic': 'red'}
        
        for scenario, data in forecasts_dict.items():
            if data is not None:
                forecast_years = pd.to_datetime(data['year'], format='%Y')
                
                fig.add_trace(go.Scatter(
                    x=forecast_years,
                    y=data['value'],
                    mode='lines+markers',
                    name=scenario.title(),
                    line=dict(color=colors.get(scenario, 'gray'), width=3),
                    marker=dict(size=8),
                    hovertemplate=f'Scenario: {scenario}<br>Year: %{{x|%Y}}<br>Value: %{{y:.1f}}%<extra></extra>'
                ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            xaxis_title="Year",
            yaxis_title="Percentage (%)",
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def create_event_impact_chart(impact_data, title):
        """Create bar chart of event impacts"""
        fig = go.Figure()
        
        # Sort by impact magnitude
        impact_data = impact_data.sort_values('Impact (pp)', ascending=False)
        
        # Color by direction
        colors = ['green' if x > 0 else 'red' for x in impact_data['Impact (pp)']]
        
        fig.add_trace(go.Bar(
            x=impact_data['Event'],
            y=impact_data['Impact (pp)'],
            marker_color=colors,
            text=impact_data['Impact (pp)'].apply(lambda x: f'{x:+.1f}pp'),
            textposition='outside',
            hovertemplate='Event: %{x}<br>Impact: %{y:+.1f}pp<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            xaxis_title="Event",
            yaxis_title="Impact (percentage points)",
            template='plotly_white',
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(value, title, min_val=0, max_val=100, target=None):
        """Create gauge chart for progress visualization"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title},
            delta={'reference': target} if target else None,
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [min_val, max_val*0.6], 'color': "lightgray"},
                    {'range': [max_val*0.6, max_val*0.8], 'color': "gray"},
                    {'range': [max_val*0.8, max_val], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': target if target else max_val
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig