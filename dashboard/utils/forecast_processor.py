"""
Forecast processing utilities
"""
import pandas as pd
import numpy as np

class ForecastProcessor:
    """Processes and analyzes forecast data"""
    
    @staticmethod
    def calculate_growth_rates(historical_value, forecast_values):
        """Calculate growth rates from historical to forecast"""
        if historical_value is None or forecast_values is None:
            return None
        
        growth = {}
        for year, forecast in forecast_values.items():
            growth[year] = forecast - historical_value
        
        return growth
    
    @staticmethod
    def calculate_annual_growth_rate(start_value, end_value, years):
        """Calculate annual compound growth rate"""
        if start_value <= 0 or years <= 0:
            return None
        
        cagr = ((end_value / start_value) ** (1/years) - 1) * 100
        return cagr
    
    @staticmethod
    def get_milestones(forecast_data, milestones=[50, 60, 70, 80, 90]):
        """Get years when milestones will be reached"""
        if forecast_data is None or len(forecast_data) < 2:
            return None
        
        milestone_years = {}
        
        for milestone in milestones:
            # Find when forecast crosses milestone
            for i in range(len(forecast_data) - 1):
                year1 = forecast_data.iloc[i]['year']
                value1 = forecast_data.iloc[i]['value']
                year2 = forecast_data.iloc[i + 1]['year']
                value2 = forecast_data.iloc[i + 1]['value']
                
                if value1 <= milestone <= value2:
                    # Linear interpolation
                    fraction = (milestone - value1) / (value2 - value1)
                    milestone_year = year1 + fraction * (year2 - year1)
                    milestone_years[milestone] = round(milestone_year, 1)
                    break
        
        return milestone_years
    
    @staticmethod
    def analyze_nfis_target_gap(current_value, forecast_2025, target_2025=70):
        """Analyze gap to NFIS-II target"""
        if current_value is None or forecast_2025 is None:
            return None
        
        gap = target_2025 - forecast_2025
        achievement_pct = (forecast_2025 / target_2025) * 100
        status = "On Track" if gap <= 0 else "Off Track"
        
        return {
            'current_value': current_value,
            'forecast_2025': forecast_2025,
            'target_2025': target_2025,
            'gap': gap,
            'achievement_pct': achievement_pct,
            'status': status
        }