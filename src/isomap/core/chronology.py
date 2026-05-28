"""chronology.py — Date format detection and normalisation.
exports: normalise_age(value, source_format, target_format) -> float
used_by: main.py
rules:
Must handle conversion between BP, cal BP, and BCE/CE using 1950 anchor.
"""

import pandas as pd
import re
from typing import Any, Optional, Dict, Tuple

def detect_age_format(column_name: str) -> str:
    """Heuristics to detect the time format from a column name."""
    col_lower = column_name.lower()
    if re.search(r'14c|uncal', col_lower):
        return '14C_BP'
    if re.search(r'cal.*bp', col_lower):
        return 'cal_BP'
    if re.search(r'bce|ce|ad|bc', col_lower):
        return 'CE'
    if re.search(r'ka|kyr', col_lower):
        return 'ka'
    if re.search(r'ma|myr', col_lower):
        return 'Ma'
    return 'unknown'

def parse_age_string(value: Any) -> Optional[float]:
    """Parse age from string that may contain characters like ~, <, >, etc."""
    if pd.isna(value):
        return None
        
    if isinstance(value, (int, float)):
        return float(value)
        
    s = str(value).strip()
    # Extract first numeric sequence (including optional minus sign and decimals)
    match = re.search(r'-?\d+\.?\d*', s)
    if match:
        return float(match.group(0))
        
    return None

def normalise_age(value: Any, source_format: str, target_format: str = 'cal_BP') -> Optional[float]:
    """
    Normalises an age from source_format to target_format.
    Anchor year for BP is 1950 CE.
    14C_BP is considered uncalibrated, but for simple normalisation we often
    just keep it or treat it loosely as BP if calibration isn't requested.
    This function primarily converts cal_BP <-> CE <-> ka/Ma.
    """
    val = parse_age_string(value)
    if val is None:
        return None
        
    # Convert everything to a base format (cal_BP) first
    cal_bp = None
    if source_format == 'cal_BP' or source_format == '14C_BP' or source_format == 'unknown':
        cal_bp = val
    elif source_format == 'CE':
        # cal_BP = 1950 - CE
        cal_bp = 1950.0 - val
    elif source_format == 'BCE':
        # BCE is practically negative CE
        cal_bp = 1950.0 - (-val)
    elif source_format == 'ka':
        cal_bp = val * 1000.0
    elif source_format == 'Ma':
        cal_bp = val * 1_000_000.0
    else:
        cal_bp = val
        
    # Convert from cal_bp to target_format
    if target_format == 'cal_BP' or target_format == '14C_BP' or target_format == 'unknown':
        return cal_bp
    elif target_format == 'CE':
        return 1950.0 - cal_bp
    elif target_format == 'BCE':
        return -(1950.0 - cal_bp)
    elif target_format == 'ka':
        return cal_bp / 1000.0
    elif target_format == 'Ma':
        return cal_bp / 1_000_000.0
        
    return cal_bp

def process_chronology_dataframe(df: pd.DataFrame, mappings: Dict[str, Tuple[str, str]]) -> pd.DataFrame:
    """
    Applies age normalisation across the dataframe.
    mappings is dict of: target_column -> (source_column, source_format)
    """
    out_df = df.copy()
    
    for target_col, (source_col, source_format) in mappings.items():
        if source_col in out_df.columns:
            # For this MVP, we assume target is cal_BP unless specified
            out_df[target_col] = out_df[source_col].apply(lambda x: normalise_age(x, source_format, 'cal_BP'))
            
    return out_df
