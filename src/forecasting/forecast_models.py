"""
Forecasting models for Ethiopia financial inclusion
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

class FinancialInclusionForecaster:
    """Main class for forecasting financial inclusion indicators"""
    
    def __init__(self, enriched_data_path: str, association_matrix_path: str):
        """
        Initialize forecaster
        
        Args:
            enriched_data_path: Path to enriched dataset
            association_matrix_path: Path to event-impact association matrix
        """
        self.data = pd.read_csv(enriched_data_path)
        self.association_matrix = pd.read_csv(association_matrix_path, index_col=0)
        self.forecasts = {}
        self.scenarios = {}
        
    def prepare_historical_data(self, indicator: str) -> pd.DataFrame:
        """Prepare historical time series for an indicator"""
        # Filter for the indicator
        indicator_data = self.data[
            (self.data['record_type'] == 'observation') & 
            (self.data['indicator'] == indicator)
        ].copy()
        
        if indicator_data.empty:
            raise ValueError(f"No historical data found for indicator: {indicator}")
        
        # Convert to time series
        indicator_data['date'] = pd.to_datetime(indicator_data['observation_date'])
        indicator_data = indicator_data.sort_values('date')
        
        # Aggregate by year (take mean if multiple values per year)
        indicator_data['year'] = indicator_data['date'].dt.year
        yearly_data = indicator_data.groupby('year')['value_numeric'].mean().reset_index()
        
        return yearly_data
    
    def baseline_forecast(self, indicator: str, forecast_years: list = [2025, 2026, 2027]):
        """Create baseline forecast using linear regression"""
        
        # Get historical data
        historical = self.prepare_historical_data(indicator)
        
        if len(historical) < 2:
            raise ValueError(f"Insufficient historical data for {indicator}")
        
        # Linear regression model
        X = historical['year'].values.reshape(-1, 1)
        y = historical['value_numeric'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate forecasts
        forecast_df = pd.DataFrame({'year': forecast_years})
        forecast_df['baseline'] = model.predict(forecast_df[['year']])
        
        # Calculate confidence intervals
        y_pred = model.predict(X)
        residuals = y - y_pred
        std_error = np.std(residuals)
        
        forecast_df['baseline_lower'] = forecast_df['baseline'] - 1.96 * std_error
        forecast_df['baseline_upper'] = forecast_df['baseline'] + 1.96 * std_error
        
        return forecast_df
    
    def event_augmented_forecast(self, indicator: str, forecast_years: list = [2025, 2026, 2027]):
        """Create forecast incorporating event impacts"""
        
        # Start with baseline
        baseline_df = self.baseline_forecast(indicator, forecast_years)
        
        # Get event impacts for this indicator
        if indicator not in self.association_matrix.columns:
            print(f"No event impacts found for {indicator}, returning baseline")
            baseline_df['event_augmented'] = baseline_df['baseline']
            return baseline_df
        
        # Calculate cumulative event impacts
        event_impacts = self.association_matrix[indicator]
        active_events = event_impacts[event_impacts != 0]
        
        if active_events.empty:
            print(f"No active event impacts for {indicator}, returning baseline")
            baseline_df['event_augmented'] = baseline_df['baseline']
            return baseline_df
        
        # Get event dates
        events = self.data[self.data['record_type'] == 'event'].copy()
        events['date'] = pd.to_datetime(events['observation_date'])
        
        # Calculate event effects for each forecast year
        event_effects = {}
        for year in forecast_years:
            year_effect = 0
            year_date = pd.Timestamp(f'{year}-01-01')
            
            for event_name, impact in active_events.items():
                # Find event date
                event_row = events[events['indicator'] == event_name]
                if not event_row.empty:
                    event_date = event_row['date'].iloc[0]
                    
                    # Calculate time since event (in years)
                    years_since = (year_date - event_date).days / 365.25
                    
                    if years_since > 0:
                        # Apply impact with 2-year ramp-up (gradual effect)
                        effect_factor = min(1.0, years_since / 2)
                        year_effect += impact * effect_factor
            
            event_effects[year] = year_effect
        
        # Apply event effects
        baseline_df['event_augmented'] = baseline_df['baseline'] + baseline_df['year'].map(event_effects)
        baseline_df['event_lower'] = baseline_df['event_augmented'] - 1.96 * np.std(list(event_effects.values()))
        baseline_df['event_upper'] = baseline_df['event_augmented'] + 1.96 * np.std(list(event_effects.values()))
        
        return baseline_df
    
    def create_scenarios(self, indicator: str, forecast_years: list = [2025, 2026, 2027]):
        """Create optimistic, base, and pessimistic scenarios"""
        
        # Get event-augmented forecast as base scenario
        base_df = self.event_augmented_forecast(indicator, forecast_years)
        
        # Scenario multipliers
        optimistic_mult = 1.2  # 20% better than expected
        pessimistic_mult = 0.8  # 20% worse than expected
        
        scenarios_df = base_df[['year']].copy()
        
        # Base scenario (event-augmented)
        scenarios_df['base'] = base_df['event_augmented']
        scenarios_df['base_lower'] = base_df['event_lower']
        scenarios_df['base_upper'] = base_df['event_upper']
        
        # Optimistic scenario
        scenarios_df['optimistic'] = base_df['event_augmented'] * optimistic_mult
        scenarios_df['optimistic_lower'] = base_df['event_lower'] * optimistic_mult
        scenarios_df['optimistic_upper'] = base_df['event_upper'] * optimistic_mult
        
        # Pessimistic scenario
        scenarios_df['pessimistic'] = base_df['event_augmented'] * pessimistic_mult
        scenarios_df['pessimistic_lower'] = base_df['event_lower'] * pessimistic_mult
        scenarios_df['pessimistic_upper'] = base_df['event_upper'] * pessimistic_mult
        
        # Ensure values don't exceed 100%
        for col in ['base', 'optimistic', 'pessimistic', 
                   'base_lower', 'optimistic_lower', 'pessimistic_lower',
                   'base_upper', 'optimistic_upper', 'pessimistic_upper']:
            scenarios_df[col] = scenarios_df[col].clip(upper=100)
            scenarios_df[col] = scenarios_df[col].clip(lower=0)
        
        return scenarios_df
    
    def forecast_all_indicators(self):
        """Forecast all key indicators"""
        
        key_indicators = {
            'Account Ownership Rate': 'Access',
            'USG_DIGITAL_PAYMENT': 'Usage'
        }
        
        all_forecasts = {}
        
        for indicator, pillar in key_indicators.items():
            print(f"Forecasting {indicator} ({pillar})...")
            
            try:
                # Get scenarios
                scenarios = self.create_scenarios(indicator)
                all_forecasts[indicator] = {
                    'pillar': pillar,
                    'scenarios': scenarios,
                    'latest_historical': self.get_latest_value(indicator)
                }
                
                print(f"  ✓ Completed: {len(scenarios)} forecast years")
                
            except Exception as e:
                print(f"  ✗ Error forecasting {indicator}: {str(e)}")
                all_forecasts[indicator] = None
        
        self.forecasts = all_forecasts
        return all_forecasts
    
    def get_latest_value(self, indicator: str):
        """Get latest historical value for an indicator"""
        historical = self.prepare_historical_data(indicator)
        if not historical.empty:
            return historical.iloc[-1]['value_numeric']
        return None
    
    def generate_forecast_summary(self):
        """Generate comprehensive forecast summary"""
        
        if not self.forecasts:
            self.forecast_all_indicators()
        
        summary = []
        
        for indicator, data in self.forecasts.items():
            if data is None:
                continue
                
            scenarios_df = data['scenarios']
            latest_value = data['latest_historical']
            
            for _, row in scenarios_df.iterrows():
                summary.append({
                    'Year': row['year'],
                    'Indicator': indicator,
                    'Pillar': data['pillar'],
                    'Latest Historical': latest_value,
                    'Base Forecast': row['base'],
                    'Optimistic Forecast': row['optimistic'],
                    'Pessimistic Forecast': row['pessimistic'],
                    'Base Range': f"{row['base_lower']:.1f}-{row['base_upper']:.1f}",
                    'Growth from 2024 (Base)': f"{(row['base'] - latest_value):+.1f}pp" if latest_value else "N/A"
                })
        
        return pd.DataFrame(summary)
    
    def calculate_nfis_target_gap(self):
        """Calculate gap to NFIS-II targets (70% by 2025)"""
        
        if 'Account Ownership Rate' not in self.forecasts:
            self.forecast_all_indicators()
        
        ownership_forecast = self.forecasts['Account Ownership Rate']['scenarios']
        nfis_target_2025 = 70.0
        
        # Find 2025 forecast
        forecast_2025 = ownership_forecast[ownership_forecast['year'] == 2025]
        
        if not forecast_2025.empty:
            base_2025 = forecast_2025['base'].iloc[0]
            gap = nfis_target_2025 - base_2025
            
            return {
                'NFIS-II Target (2025)': nfis_target_2025,
                'Base Forecast (2025)': base_2025,
                'Gap': gap,
                'Achievement %': (base_2025 / nfis_target_2025) * 100,
                'Status': 'On Track' if gap <= 0 else 'Off Track'
            }
        
        return None