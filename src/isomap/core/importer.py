"""importer.py — Parses legacy datasets from CSV and Excel with encoding detection.
exports: read_dataset(file_path, sheet_name) -> pd.DataFrame, get_sheet_names(file_path) -> list[str]
used_by: main.py -> read_dataset
rules:
Must handle missing encodings using chardet.
"""

import pandas as pd
import chardet
from pathlib import Path
from typing import Optional, Union, List

def detect_encoding(file_path: Union[str, Path]) -> str:
    """Detect the character encoding of a file using chardet."""
    with open(file_path, 'rb') as f:
        # Read a chunk to guess encoding (100KB is usually enough)
        raw_data = f.read(100000)
    result = chardet.detect(raw_data)
    # Default to utf-8 if detection fails or confidence is low
    if result['encoding'] is None or result['confidence'] < 0.5:
        return 'utf-8'
    return result['encoding']

def get_sheet_names(file_path: Union[str, Path]) -> List[str]:
    """Return a list of sheet names if the file is an Excel workbook, else empty list."""
    path = Path(file_path)
    if path.suffix.lower() in ['.xlsx', '.xls']:
        engine = 'openpyxl' if path.suffix.lower() == '.xlsx' else 'xlrd'
        try:
            xl = pd.ExcelFile(path, engine=engine)
            return xl.sheet_names
        except Exception:
            return []
    return []

def read_dataset(file_path: Union[str, Path], sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    Read a CSV or Excel file into a Pandas DataFrame.
    Automatically detects encoding for CSV files.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix == '.csv':
        encoding = detect_encoding(path)
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            # Fallback to a generous encoding if detection was wrong
            return pd.read_csv(path, encoding='latin-1', on_bad_lines='skip')
            
    elif suffix in ['.xlsx', '.xls']:
        engine = 'openpyxl' if suffix == '.xlsx' else 'xlrd'
        return pd.read_excel(path, sheet_name=sheet_name or 0, engine=engine)
        
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Only .csv, .xlsx, and .xls are supported.")
