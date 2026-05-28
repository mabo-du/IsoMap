"""distribution.py — Infers column types based on value distribution and heuristics.
exports: infer_column_types(df) -> dict
used_by: mapper.py -> infer_column_types
rules:
Must handle missing (NaN) values gracefully.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, Any

def _infer_series_type(series: pd.Series) -> Dict[str, Any]:
    """Infers the semantic type of a single pandas Series."""
    s = series.dropna()
    if s.empty:
        return {"type": "unknown", "confidence": "low"}

    is_numeric = pd.api.types.is_numeric_dtype(s)
    
    if is_numeric:
        # Latitude
        if s.between(-90, 90).all() and series.name and 'lat' in series.name.lower():
            return {"type": "latitude", "confidence": "high"}
        # Longitude
        if s.between(-180, 180).all() and series.name and 'lon' in series.name.lower():
            return {"type": "longitude", "confidence": "high"}
            
        # Isotopic values
        if s.between(-35, 5).mean() > 0.8: # mostly in range
            return {"type": "d13C", "confidence": "medium"}
            
        if s.between(-5, 25).mean() > 0.8:
            return {"type": "d15N", "confidence": "medium"}
            
        if s.between(-15, 5).mean() > 0.8:
            return {"type": "d18O", "confidence": "medium"}
            
        if s.between(0.700, 0.750).mean() > 0.9:
            return {"type": "87Sr/86Sr", "confidence": "high"}
            
        # C:N ratio
        if s.between(2.5, 4.5).mean() > 0.9:
            return {"type": "C:N ratio", "confidence": "high"}
            
        # 14C BP
        if (s >= 0).all() and (s <= 60000).all() and (s.mean() > 500):
            return {"type": "14C BP", "confidence": "medium"}
            
    else:
        # String matching
        s_str = s.astype(str)
        
        # Lab codes (e.g., OxA-12345, UGAMS-9876)
        lab_code_pattern = re.compile(r'^[A-Za-z]+-\d+$')
        if s_str.str.match(lab_code_pattern).mean() > 0.5:
            return {"type": "lab_code", "confidence": "high"}
            
        # Taxon name (Genus species)
        taxon_pattern = re.compile(r'^[A-Z][a-z]+\s[a-z]+$')
        if s_str.str.match(taxon_pattern).mean() > 0.5:
            return {"type": "taxon_name", "confidence": "medium"}

    return {"type": "unknown", "confidence": "low"}

def infer_column_types(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Infers the semantic type of each column in a DataFrame based on value distributions.
    Returns a dictionary mapping column names to {"type": str, "confidence": str}.
    """
    results = {}
    for col in df.columns:
        results[col] = _infer_series_type(df[col])
    return results
