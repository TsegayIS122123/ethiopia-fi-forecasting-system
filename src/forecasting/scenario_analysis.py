"""
Scenario analysis for financial inclusion forecasts
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List

class ScenarioAnalyzer:
    """Analyze and visualize forecast scenarios"""
    
    def __init__(self, forecasts: Dict):
        self.forecasts = forecasts
        self.scenarios_summary = None
        
    def create_scenario_summary(self) -> pd.DataFrame:
        """Create summary of all scenarios"""
        
        summary_data = []
        
        for indicator, data in self.forecasts.items():
            if data is None:
                continue
                
            scenarios_df = data['scenarios']
            latest_value = data['latest_historical']
            
            # Calculate key metrics for each scenario
            for scenario in ['base', 'optimistic', 'pessimistic']:
                for _, row in scenarios_df.iterrows():
                    summary_data.append({
                        'Year': row['year'],
                        'Indicator': indicator,
                        'Scenario': scenario,
                        'Forecast': row[scenario],
                        'Lower Bound': row[f'{scenario}_lower'],
                        'Upper Bound': row[f'{scenario}_upper'],
                        'Latest Historical': latest_value
                    })
        
        self.scenarios_summary = pd.DataFrame(summary_data)
        return self.scenarios_summary
    
    def plot_forecast_timeline(self, indicator: str, save_path: str = None):
        """Plot forecast timeline with scenarios"""
        
        if indicator not in self.forecasts:
            raise ValueError(f"No forecasts found for {indicator}")
        
        data = self.forecasts[indicator]
        scenarios_df = data['scenarios']
        latest_value = data['latest_historical']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot scenarios
        years = scenarios_df['year']
        
        # Base scenario
        ax.plot(years, scenarios_df['base'], 'b-', linewidth=2, label='Base Scenario')
        ax.fill_between(years, 
                       scenarios_df['base_lower'], 
                       scenarios_df['base_upper'], 
                       alpha=0.2, color='blue')
        
        # Optimistic scenario
        ax.plot(years, scenarios_df['optimistic'], 'g--', linewidth=2, label='Optimistic')
        ax.fill_between(years, 
                       scenarios_df['optimistic_lower'], 
                       scenarios_df['optimistic_upper'], 
                       alpha=0.1, color='green')
        
        # Pessimistic scenario
        ax.plot(years, scenarios_df['pessimistic'], 'r--', linewidth=2, label='Pessimistic')
        ax.fill_between(years, 
                       scenarios_df['pessimistic_lower'], 
                       scenarios_df['pessimistic_upper'], 
                       alpha=0.1, color='red')
        
        # Add historical point
        if latest_value is not None:
            ax.scatter(2024, latest_value, color='black', s=100, zorder=5, 
                      label=f'2024 Actual: {latest_value:.1f}%')
        
        # Customize plot
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel(f'{indicator} (%)', fontsize=12)
        ax.set_title(f'{indicator} Forecast: 2025-2027', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Add confidence interval labels
        ax.text(0.02, 0.98, 'Shaded areas = 95% confidence intervals', 
               transform=ax.transAxes, fontsize=10, 
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        return fig, ax
    
    def calculate_growth_rates(self) -> pd.DataFrame:
        """Calculate annual growth rates by scenario"""
        
        if self.scenarios_summary is None:
            self.create_scenario_summary()
        
        growth_data = []
        
        for indicator in self.forecasts.keys():
            if self.forecasts[indicator] is None:
                continue
                
            scenarios_df = self.forecasts[indicator]['scenarios']
            latest_value = self.forecasts[indicator]['latest_historical']
            
            if latest_value is None:
                continue
            
            for scenario in ['base', 'optimistic', 'pessimistic']:
                # Calculate growth from 2024 to each forecast year
                for year in [2025, 2026, 2027]:
                    forecast_value = scenarios_df[scenarios_df['year'] == year][scenario].iloc[0]
                    growth = forecast_value - latest_value
                    growth_pct = (growth / latest_value) * 100 if latest_value > 0 else 0
                    
                    growth_data.append({
                        'Indicator': indicator,
                        'Scenario': scenario,
                        'Year': year,
                        'Forecast': forecast_value,
                        'Growth (pp)': growth,
                        'Growth (%)': growth_pct,
                        'Cumulative Growth (2024-2027)': None  # Will fill later
                    })
        
        growth_df = pd.DataFrame(growth_data)
        
        # Calculate cumulative growth
        for indicator in growth_df['Indicator'].unique():
            for scenario in growth_df['Scenario'].unique():
                mask = (growth_df['Indicator'] == indicator) & (growth_df['Scenario'] == scenario)
                if mask.any():
                    cumulative = growth_df.loc[mask, 'Growth (pp)'].sum()
                    growth_df.loc[mask, 'Cumulative Growth (2024-2027)'] = cumulative
        
        return growth_df
    
    def identify_key_drivers(self, association_matrix: pd.DataFrame) -> pd.DataFrame:
        """Identify key events driving forecast outcomes"""
        
        driver_analysis = []
        
        for indicator in ['Account Ownership Rate', 'USG_DIGITAL_PAYMENT']:
            if indicator in association_matrix.columns:
                impacts = association_matrix[indicator]
                significant_events = impacts[impacts != 0].sort_values(ascending=False)
                
                for event, impact in significant_events.items():
                    driver_analysis.append({
                        'Indicator': indicator,
                        'Event': event,
                        'Impact (pp)': impact,
                        'Magnitude': 'High' if abs(impact) >= 10 else 'Medium' if abs(impact) >= 5 else 'Low',
                        'Direction': 'Positive' if impact > 0 else 'Negative'
                    })
        
        return pd.DataFrame(driver_analysis)
    
    def generate_uncertainty_assessment(self) -> Dict:
        """Assess forecast uncertainty"""
        
        uncertainty = {
            'data_quality': {
                'historical_points': 'Limited (5 Findex points)',
                'confidence': 'Medium',
                'impact': 'Wider confidence intervals'
            },
            'model_uncertainty': {
                'trend_assumption': 'Linear continuation',
                'event_impact_validation': '95.9% accuracy',
                'lag_assumption': 'Based on comparable evidence'
            },
            'external_factors': {
                'policy_changes': 'High uncertainty',
                'economic_conditions': 'Medium uncertainty',
                'technology_adoption': 'Low to medium uncertainty'
            },
            'recommendations': [
                'Monitor quarterly infrastructure data',
                'Update with 2025 survey results',
                'Track actual vs forecast monthly'
            ]
        }
        
        return uncertainty