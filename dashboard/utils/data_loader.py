"""
Data loading utilities for the dashboard
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

class DashboardDataLoader:
    """Loads and prepares data for the dashboard"""
    
    def __init__(self):
        self.enriched_data = None
        self.forecasts = None
        self.association_matrix = None
        self.event_impacts = None
        self.validation_results = None
        self.summary_stats = {}
        
    def load_all_data(self):
        """Load all required data files"""
        try:
            # Get base directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Load enriched data
            enriched_path = os.path.join(base_dir, 'data', 'processed', 'ethiopia_fi_enriched.csv')
            if os.path.exists(enriched_path):
                self.enriched_data = pd.read_csv(enriched_path, encoding='utf-8')
                print(f"✓ Loaded enriched data: {len(self.enriched_data)} records")
            else:
                print(f"✗ Enriched data not found: {enriched_path}")
                return False
            
            # Load forecasts - use try/except for each file
            self.forecasts = {}
            forecast_files = {
                'account_ownership': 'account_ownership_forecast.csv',
                'account_ownership_scenarios': 'account_ownership_scenarios.csv',
                'digital_payments': 'digital_payment_forecast.csv',
                'digital_payment_scenarios': 'digital_payment_scenarios.csv',
                'summary': 'forecast_summary.csv'
            }
            
            for key, filename in forecast_files.items():
                filepath = os.path.join(base_dir, 'models', filename)
                try:
                    if os.path.exists(filepath):
                        self.forecasts[key] = pd.read_csv(filepath)
                        print(f"✓ Loaded forecast: {filename}")
                    else:
                        print(f"⚠ Forecast not found: {filename}")
                        self.forecasts[key] = None
                except Exception as e:
                    print(f"✗ Error loading {filename}: {str(e)}")
                    self.forecasts[key] = None
            
            # Load association matrix
            matrix_path = os.path.join(base_dir, 'models', 'association_matrix.csv')
            if os.path.exists(matrix_path):
                self.association_matrix = pd.read_csv(matrix_path, index_col=0)
                print(f"✓ Loaded association matrix")
            else:
                print("⚠ Association matrix not found")
                self.association_matrix = None
            
            # Load impact summary
            impact_path = os.path.join(base_dir, 'models', 'impact_summary.csv')
            if os.path.exists(impact_path):
                self.event_impacts = pd.read_csv(impact_path)
                print(f"✓ Loaded impact summary: {len(self.event_impacts)} records")
            else:
                print("⚠ Impact summary not found")
                self.event_impacts = None
            
            # Load validation results
            validation_path = os.path.join(base_dir, 'models', 'validation_results.csv')
            if os.path.exists(validation_path):
                self.validation_results = pd.read_csv(validation_path)
                print(f"✓ Loaded validation results")
            else:
                print("⚠ Validation results not found")
                self.validation_results = None
            
            # Calculate summary statistics
            self._calculate_summary_stats()
            
            print("✅ All data loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def _calculate_summary_stats(self):
        """Calculate key summary statistics"""
        
        # Latest account ownership
        if self.enriched_data is not None:
            account_data = self.enriched_data[
                (self.enriched_data['indicator'] == 'Account Ownership Rate') &
                (self.enriched_data['record_type'] == 'observation')
            ]
            if not account_data.empty:
                account_data = account_data.sort_values('observation_date')
                self.summary_stats['latest_account_ownership'] = account_data['value_numeric'].iloc[-1]
                self.summary_stats['account_ownership_year'] = account_data['observation_date'].iloc[-1][:4]
        
        # Latest digital payments
        if self.enriched_data is not None:
            digital_data = self.enriched_data[
                (self.enriched_data['indicator'].str.contains('Digital Payment', na=False)) &
                (self.enriched_data['record_type'] == 'observation')
            ]
            if not digital_data.empty:
                digital_data = digital_data.sort_values('observation_date')
                self.summary_stats['latest_digital_payments'] = digital_data['value_numeric'].iloc[-1]
        
        # Gender gap
        if self.enriched_data is not None:
            gender_data_2021 = self.enriched_data[
                (self.enriched_data['indicator'] == 'Account Ownership Rate') &
                (self.enriched_data['gender'].isin(['male', 'female'])) &
                (self.enriched_data['observation_date'].str.contains('2021'))
            ]
            if len(gender_data_2021) >= 2:
                male_val = gender_data_2021[gender_data_2021['gender'] == 'male']['value_numeric'].values[0]
                female_val = gender_data_2021[gender_data_2021['gender'] == 'female']['value_numeric'].values[0]
                self.summary_stats['gender_gap'] = male_val - female_val
        
        # P2P/ATM ratio
        if self.enriched_data is not None:
            p2p_data = self.enriched_data[
                (self.enriched_data['indicator'] == 'P2P Transaction Count') &
                (self.enriched_data['record_type'] == 'observation')
            ]
            atm_data = self.enriched_data[
                (self.enriched_data['indicator'] == 'ATM Transaction Count') &
                (self.enriched_data['record_type'] == 'observation')
            ]
            
            if not p2p_data.empty and not atm_data.empty:
                p2p_data = p2p_data.sort_values('observation_date')
                atm_data = atm_data.sort_values('observation_date')
                
                latest_p2p = p2p_data['value_numeric'].iloc[-1]
                latest_atm = atm_data['value_numeric'].iloc[-1]
                
                if latest_atm > 0:
                    self.summary_stats['p2p_atm_ratio'] = latest_p2p / latest_atm
                    self.summary_stats['p2p_surpasses_atm'] = latest_p2p > latest_atm
        
        # Forecast growth
        if 'account_ownership' in self.forecasts and self.forecasts['account_ownership'] is not None:
            forecast_2027 = self.forecasts['account_ownership'][self.forecasts['account_ownership']['year'] == 2027]
            if not forecast_2027.empty and 'latest_account_ownership' in self.summary_stats:
                growth = forecast_2027['base'].iloc[0] - self.summary_stats['latest_account_ownership']
                self.summary_stats['projected_growth_2027'] = growth
    
    def get_indicator_timeseries(self, indicator_name):
        """Get time series data for an indicator"""
        if self.enriched_data is None:
            return None
        
        indicator_data = self.enriched_data[
            (self.enriched_data['indicator'] == indicator_name) &
            (self.enriched_data['record_type'] == 'observation')
        ].copy()
        
        if indicator_data.empty:
            return None
        
        indicator_data['date'] = pd.to_datetime(indicator_data['observation_date'])
        indicator_data = indicator_data.sort_values('date')
        
        return indicator_data[['date', 'value_numeric', 'gender', 'location', 'source_name']]
    
    def get_events_timeline(self):
        """Get timeline of events"""
        if self.enriched_data is None:
            return None
        
        events = self.enriched_data[self.enriched_data['record_type'] == 'event'].copy()
        if events.empty:
            return None
        
        events['date'] = pd.to_datetime(events['observation_date'])
        events = events.sort_values('date')
        
        return events[['date', 'indicator', 'category', 'source_name']]
    
    def get_forecast_data(self, indicator, scenario='base'):
        """Get forecast data for an indicator and scenario"""
        indicator_map = {
            'Account Ownership': 'account_ownership',
            'Digital Payments': 'digital_payments'
        }
        
        if indicator not in indicator_map:
            return None
        
        forecast_key = indicator_map[indicator]
        if forecast_key not in self.forecasts or self.forecasts[forecast_key] is None:
            return None
        
        forecast_df = self.forecasts[forecast_key].copy()
        
        # Select scenario columns
        if scenario == 'base':
            value_col = 'base' if 'base' in forecast_df.columns else forecast_df.columns[1]
            lower_col = 'base_lower' if 'base_lower' in forecast_df.columns else None
            upper_col = 'base_upper' if 'base_upper' in forecast_df.columns else None
        elif scenario == 'optimistic':
            value_col = 'optimistic' if 'optimistic' in forecast_df.columns else None
            lower_col = 'optimistic_lower' if 'optimistic_lower' in forecast_df.columns else None
            upper_col = 'optimistic_upper' if 'optimistic_upper' in forecast_df.columns else None
        else:  # pessimistic
            value_col = 'pessimistic' if 'pessimistic' in forecast_df.columns else None
            lower_col = 'pessimistic_lower' if 'pessimistic_lower' in forecast_df.columns else None
            upper_col = 'pessimistic_upper' if 'pessimistic_upper' in forecast_df.columns else None
        
        # If scenario column doesn't exist, use base
        if value_col is None or value_col not in forecast_df.columns:
            value_col = 'base' if 'base' in forecast_df.columns else forecast_df.columns[1]
        
        result = forecast_df[['year', value_col]].copy()
        result.columns = ['year', 'value']
        
        if lower_col and upper_col and lower_col in forecast_df.columns and upper_col in forecast_df.columns:
            result['lower'] = forecast_df[lower_col]
            result['upper'] = forecast_df[upper_col]
        
        return result