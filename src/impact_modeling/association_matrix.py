"""
Association Matrix Builder - Creates and manages event-indicator relationships
"""
import pandas as pd
import numpy as np
from typing import Dict, List
import json

class AssociationMatrixBuilder:
    """Builds and manages event-indicator association matrices"""
    
    def __init__(self, events_df: pd.DataFrame, impact_links_df: pd.DataFrame):
        self.events = events_df
        self.impact_links = impact_links_df
        self.matrix = None
        self.evidence_base = {}
        
    def build_matrix(self, indicator_mapping: Dict[str, str] = None) -> pd.DataFrame:
        """
        Build association matrix from impact links
        
        Args:
            indicator_mapping: Optional mapping from codes to names
        
        Returns:
            Association matrix DataFrame
        """
        # Default mapping
        if indicator_mapping is None:
            indicator_mapping = {
                'ACC_OWNERSHIP': 'Account Ownership Rate',
                'ACC_MM_ACCOUNT': 'Mobile Money Account Rate',
                'USG_DIGITAL_PAYMENT': 'Digital Payment Usage Rate',
                'ACC_4G_COV': '4G Population Coverage',
                'AFF_DATA_INCOME': 'Data Affordability Index',
                'USG_P2P_COUNT': 'P2P Transaction Count',
                'GEN_GAP_ACC': 'Account Ownership Gender Gap'
            }
        
        # Get unique events and indicators
        events = self.events['indicator'].unique()
        indicators = list(indicator_mapping.values())
        
        # Initialize matrix
        matrix = pd.DataFrame(0.0, index=events, columns=indicators)
        
        # Fill matrix from impact links
        for _, link in self.impact_links.iterrows():
            # Get event name
            event_mask = self.events['record_id'] == link['parent_id']
            if not event_mask.any():
                continue
                
            event_name = self.events[event_mask]['indicator'].iloc[0]
            
            # Get indicator name
            indicator_code = link['related_indicator']
            if pd.isna(indicator_code):
                continue
                
            indicator_name = indicator_mapping.get(indicator_code)
            if not indicator_name or indicator_name not in matrix.columns:
                continue
            
            # Calculate impact value
            impact_value = self._calculate_impact_value(link)
            
            # Store in matrix
            matrix.loc[event_name, indicator_name] = impact_value
            
            # Store evidence
            self._store_evidence(event_name, indicator_name, link, impact_value)
        
        self.matrix = matrix
        return matrix
    
    def _calculate_impact_value(self, link: pd.Series) -> float:
        """Calculate quantitative impact value from link data"""
        # Use impact_estimate if available
        if pd.notna(link['impact_estimate']):
            value = float(link['impact_estimate'])
            return value if link['impact_direction'] == 'increase' else -value
        
        # Estimate based on magnitude
        magnitude_estimates = {
            'high': 15.0,
            'medium': 8.0,
            'low': 3.0
        }
        
        base_value = magnitude_estimates.get(link['impact_magnitude'], 5.0)
        return base_value if link['impact_direction'] == 'increase' else -base_value
    
    def _store_evidence(self, event_name: str, indicator_name: str, 
                       link: pd.Series, impact_value: float):
        """Store evidence for impact relationship"""
        key = f"{event_name}||{indicator_name}"
        
        self.evidence_base[key] = {
            'impact_value': impact_value,
            'direction': link['impact_direction'],
            'magnitude': link['impact_magnitude'],
            'lag_months': link['lag_months'],
            'evidence_basis': link['evidence_basis'],
            'comparable_country': link['comparable_country'],
            'confidence': link['confidence']
        }
    
    def export_matrix(self, filepath: str, format: str = 'csv'):
        """Export association matrix to file"""
        if self.matrix is None:
            raise ValueError("Matrix not built. Call build_matrix() first.")
        
        if format == 'csv':
            self.matrix.to_csv(filepath)
        elif format == 'json':
            matrix_dict = self.matrix.to_dict()
            with open(filepath, 'w') as f:
                json.dump(matrix_dict, f, indent=2)
        elif format == 'excel':
            self.matrix.to_excel(filepath)
    
    def export_evidence(self, filepath: str):
        """Export evidence base to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.evidence_base, f, indent=2)
    
    def get_impact_summary(self) -> pd.DataFrame:
        """Get summary of impacts by event and indicator"""
        if self.matrix is None:
            raise ValueError("Matrix not built. Call build_matrix() first.")
        
        summary = []
        for event in self.matrix.index:
            for indicator in self.matrix.columns:
                impact = self.matrix.loc[event, indicator]
                if impact != 0:
                    key = f"{event}||{indicator}"
                    evidence = self.evidence_base.get(key, {})
                    
                    summary.append({
                        'event': event,
                        'indicator': indicator,
                        'impact_value': impact,
                        'direction': 'Positive' if impact > 0 else 'Negative',
                        'magnitude': evidence.get('magnitude', 'medium'),
                        'lag_months': evidence.get('lag_months', 12),
                        'evidence_basis': evidence.get('evidence_basis', 'estimated'),
                        'confidence': evidence.get('confidence', 'medium')
                    })
        
        return pd.DataFrame(summary)