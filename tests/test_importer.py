"""test_importer.py — Unit tests for the importer module.
"""

import pandas as pd
import pytest
from pathlib import Path
from isomap.core.importer import detect_encoding, get_sheet_names, read_dataset

def test_read_csv(tmp_path):
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)
    
    result = read_dataset(file_path)
    assert len(result) == 2
    assert list(result.columns) == ['a', 'b']

def test_read_excel(tmp_path):
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    file_path = tmp_path / "test.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df.to_excel(writer, sheet_name='Sheet2', index=False)
        
    sheets = get_sheet_names(file_path)
    assert sheets == ['Sheet1', 'Sheet2']
    
    result = read_dataset(file_path, sheet_name='Sheet2')
    assert len(result) == 2
    assert list(result.columns) == ['a', 'b']

def test_read_unsupported(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported file format"):
        read_dataset(file_path)

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_dataset("nonexistent_file.csv")
