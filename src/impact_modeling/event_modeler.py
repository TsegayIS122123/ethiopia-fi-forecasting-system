"""
Event Impact Modeler - Core class for modeling event impacts on financial inclusion indicators
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

class EventImpactModeler:
    """Models the impact of events on financial inclusion indicators"""
    
    def __init__(self, enriched_data_path: str, impact_links_path: str):
        """
        Initialize the event impact modeler
        
        Args:
            enriched_data_path: Path to enriched dataset
            impact_links_path: Path to impact links dataset
        """
        self.enriched_data = pd.read_csv(enriched_data_path)
        self.impact_links = pd.read_csv(impact_links_path)
        self.events = None
        self.observations = None
        self.association_matrix = None
        self.impact_functions = {}
        
    def prepare_data(self) -> None:
        """Prepare and clean data for modeling"""
        # Separate events and observations
        self.events = self.enriched_data[self.enriched_data['record_type'] == 'event'].copy()
        self.observations = self.enriched_data[self.enriched_data['record_type'] == 'observation'].copy()
        
        # Convert dates
        self.events['event_date'] = pd.to_datetime(self.events['observation_date'])
        self.observations['obs_date'] = pd.to_datetime(self.observations['observation_date'])
        
        # Filter for key indicators
        self.key_indicators = ['Account Ownership Rate', 'Mobile Money Account Rate', 'USG_DIGITAL_PAYMENT']
        
    def create_association_matrix(self) -> pd.DataFrame:
        """
        Create event-indicator association matrix
        
        Returns:
            DataFrame with events as rows, indicators as columns
        """
        # Initialize empty matrix
        events_list = self.events['indicator'].unique()
        indicators_list = self.key_indicators
        
        # Create matrix
        matrix = pd.DataFrame(0.0, index=events_list, columns=indicators_list)
        
        # Fill with impact estimates from impact links
        for _, link in self.impact_links.iterrows():
            event_name = self.events[self.events['record_id'] == link['parent_id']]['indicator'].values
            if len(event_name) > 0:
                event_name = event_name[0]
                indicator = link['related_indicator']
                
                # Map indicator codes to names
                indicator_name = self._map_indicator_code_to_name(indicator)
                
                if indicator_name in matrix.columns and event_name in matrix.index:
                    # Convert qualitative impact to quantitative estimate
                    impact_value = self._quantify_impact(
                        link['impact_direction'],
                        link['impact_magnitude'],
                        link['impact_estimate']
                    )
                    matrix.loc[event_name, indicator_name] = impact_value
        
        self.association_matrix = matrix
        return matrix
    
    def _map_indicator_code_to_name(self, indicator_code: str) -> str:
        """Map indicator codes to full names"""
        mapping = {
            'ACC_OWNERSHIP': 'Account Ownership Rate',
            'ACC_MM_ACCOUNT': 'Mobile Money Account Rate',
            'USG_DIGITAL_PAYMENT': 'USG_DIGITAL_PAYMENT'
        }
        return mapping.get(indicator_code, indicator_code)
    
    def _quantify_impact(self, direction: str, magnitude: str, estimate: float) -> float:
        """
        Convert qualitative impact to quantitative estimate
        
        Args:
            direction: 'increase' or 'decrease'
            magnitude: 'high', 'medium', 'low'
            estimate: Numeric estimate if available
        
        Returns:
            Quantitative impact value
        """
        if pd.notna(estimate):
            return estimate if direction == 'increase' else -estimate
        
        # Default estimates based on magnitude
        magnitude_values = {
            'high': 15.0,    # 15 percentage points
            'medium': 8.0,   # 8 percentage points
            'low': 3.0       # 3 percentage points
        }
        
        base_value = magnitude_values.get(magnitude, 5.0)
        return base_value if direction == 'increase' else -base_value
    
    def model_event_effect(self, event_name: str, indicator: str, 
                          effect_type: str = 'step') -> pd.Series:
        """
        Model the effect of a single event over time
        
        Args:
            event_name: Name of the event
            indicator: Name of the indicator
            effect_type: Type of effect ('step', 'gradual', 'pulse')
        
        Returns:
            Time series of effect values
        """
        event = self.events[self.events['indicator'] == event_name].iloc[0]
        event_date = event['event_date']
        
        # Get impact magnitude from association matrix
        impact = self.association_matrix.loc[event_name, indicator]
        lag_months = self._get_lag_months(event_name, indicator)
        
        # Create time series
        dates = pd.date_range(start='2011-01-01', end='2027-12-31', freq='M')
        effect = pd.Series(0.0, index=dates)
        
        if effect_type == 'step':
            # Step function: effect starts after lag period
            effect_date = event_date + pd.DateOffset(months=lag_months)
            effect[effect.index >= effect_date] = impact
            
        elif effect_type == 'gradual':
            # Gradual effect over 12 months
            start_date = event_date + pd.DateOffset(months=lag_months)
            end_date = start_date + pd.DateOffset(months=12)
            
            mask = (effect.index >= start_date) & (effect.index <= end_date)
            months_in_period = len(effect[mask])
            
            if months_in_period > 0:
                monthly_increment = impact / months_in_period
                for i, (date, _) in enumerate(effect[mask].items()):
                    effect[date] = monthly_increment * (i + 1)
                effect[effect.index > end_date] = impact
        
        return effect
    
    def _get_lag_months(self, event_name: str, indicator: str) -> int:
        """Get lag period for event-indicator relationship"""
        # Map indicator name to code
        reverse_mapping = {
            'Account Ownership Rate': 'ACC_OWNERSHIP',
            'Mobile Money Account Rate': 'ACC_MM_ACCOUNT',
            'USG_DIGITAL_PAYMENT': 'USG_DIGITAL_PAYMENT'
        }
        
        indicator_code = reverse_mapping.get(indicator)
        if not indicator_code:
            return 12  # Default lag
        
        # Find matching impact link
        event_id = self.events[self.events['indicator'] == event_name]['record_id'].values
        if len(event_id) > 0:
            event_id = event_id[0]
            link = self.impact_links[
                (self.impact_links['parent_id'] == event_id) & 
                (self.impact_links['related_indicator'] == indicator_code)
            ]
            if not link.empty and pd.notna(link['lag_months'].iloc[0]):
                return int(link['lag_months'].iloc[0])
        
        return 12  # Default lag
    
    def validate_historical_impacts(self) -> pd.DataFrame:
        """
        Validate impact model against historical data
        
        Returns:
            DataFrame with validation results
        """
        validation_results = []
        
        # Focus on major events with historical data
        key_events = ['Telebirr Launch', 'M-Pesa Ethiopia Launch']
        
        for event in key_events:
            for indicator in ['Account Ownership Rate', 'Mobile Money Account Rate']:
                # Get actual pre/post values
                actual_change = self._calculate_actual_change(event, indicator)
                
                # Get predicted impact
                predicted_impact = self.association_matrix.loc[event, indicator]
                
                # Calculate error
                if actual_change is not None:
                    error = abs(predicted_impact - actual_change)
                    error_pct = (error / abs(actual_change)) * 100 if actual_change != 0 else None
                    
                    validation_results.append({
                        'event': event,
                        'indicator': indicator,
                        'actual_change': actual_change,
                        'predicted_impact': predicted_impact,
                        'error': error,
                        'error_pct': error_pct,
                        'validation': 'PASS' if error_pct and error_pct < 50 else 'FAIL'
                    })
        
        return pd.DataFrame(validation_results)
    
    def _calculate_actual_change(self, event: str, indicator: str) -> Optional[float]:
        """Calculate actual change in indicator around event"""
        event_row = self.events[self.events['indicator'] == event].iloc[0]
        event_date = event_row['event_date']
        event_year = event_date.year
        
        # Get indicator data
        indicator_data = self.observations[self.observations['indicator'] == indicator].copy()
        
        if len(indicator_data) < 2:
            return None
        
        # Find closest years before and after event
        indicator_data['year'] = indicator_data['obs_date'].dt.year
        years = indicator_data['year'].unique()
        
        pre_years = [y for y in years if y < event_year]
        post_years = [y for y in years if y > event_year]
        
        if not pre_years or not post_years:
            return None
        
        pre_year = max(pre_years)
        post_year = min(post_years)
        
        pre_value = indicator_data[indicator_data['year'] == pre_year]['value_numeric'].mean()
        post_value = indicator_data[indicator_data['year'] == post_year]['value_numeric'].mean()
        
        return post_value - pre_value
    
    def visualize_impacts(self, save_path: str = None) -> None:
        """Create visualization of event impacts"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Association matrix heatmap
        plt.subplot(2, 2, 1)
        sns.heatmap(self.association_matrix, annot=True, cmap='RdYlGn', 
                   center=0, fmt='.1f', ax=axes[0, 0])
        axes[0, 0].set_title('Event-Indicator Association Matrix')
        axes[0, 0].set_xlabel('Indicators')
        axes[0, 0].set_ylabel('Events')
        
        # 2. Event timeline with impacts
        plt.subplot(2, 2, 2)
        self._plot_event_timeline(axes[0, 1])
        
        # 3. Cumulative impact over time
        plt.subplot(2, 2, 3)
        self._plot_cumulative_impact(axes[1, 0])
        
        # 4. Validation results
        plt.subplot(2, 2, 4)
        self._plot_validation_results(axes[1, 1])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def _plot_event_timeline(self, ax):
        """Plot event timeline with impact magnitudes"""
        event_dates = []
        event_names = []
        impacts = []
        
        for event_name in self.association_matrix.index:
            event_row = self.events[self.events['indicator'] == event_name].iloc[0]
            total_impact = self.association_matrix.loc[event_name].sum()
            
            event_dates.append(event_row['event_date'])
            event_names.append(event_name)
            impacts.append(total_impact)
        
        # Sort by date
        sorted_idx = np.argsort(event_dates)
        event_dates = [event_dates[i] for i in sorted_idx]
        event_names = [event_names[i] for i in sorted_idx]
        impacts = [impacts[i] for i in sorted_idx]
        
        # Plot
        colors = ['green' if imp > 0 else 'red' for imp in impacts]
        ax.bar(range(len(event_dates)), impacts, color=colors)
        ax.set_xticks(range(len(event_dates)))
        ax.set_xticklabels([d.strftime('%Y-%m') for d in event_dates], rotation=45)
        ax.set_ylabel('Total Impact (pp)')
        ax.set_title('Event Timeline with Total Impacts')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    def _plot_cumulative_impact(self, ax):
        """Plot cumulative impact over time"""
        dates = pd.date_range(start='2011-01-01', end='2027-12-31', freq='M')
        cumulative_impact = pd.Series(0.0, index=dates)
        
        for event_name in self.association_matrix.index:
            for indicator in self.association_matrix.columns:
                effect = self.model_event_effect(event_name, indicator, 'gradual')
                # Align indices
                effect = effect.reindex(dates).fillna(0)
                cumulative_impact += effect
        
        ax.plot(cumulative_impact.index, cumulative_impact.values, linewidth=2)
        ax.set_xlabel('Year')
        ax.set_ylabel('Cumulative Impact (pp)')
        ax.set_title('Cumulative Impact of All Events')
        ax.grid(True, alpha=0.3)
    
    def _plot_validation_results(self, ax):
        """Plot validation results"""
        validation_df = self.validate_historical_impacts()
        if validation_df.empty:
            ax.text(0.5, 0.5, 'No validation data available', 
                   ha='center', va='center')
            return
        
        # Plot actual vs predicted
        x = range(len(validation_df))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], validation_df['actual_change'], 
               width, label='Actual', alpha=0.7)
        ax.bar([i + width/2 for i in x], validation_df['predicted_impact'], 
               width, label='Predicted', alpha=0.7)
        
        ax.set_xticks(x)
        ax.set_xticklabels([f"{row['event'][:10]}...\n{row['indicator'][:10]}..." 
                           for _, row in validation_df.iterrows()], rotation=45)
        ax.set_ylabel('Impact (pp)')
        ax.set_title('Validation: Actual vs Predicted Impacts')
        ax.legend()
        ax.grid(True, alpha=0.3)