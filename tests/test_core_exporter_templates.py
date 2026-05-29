import pytest
import pandas as pd
from pathlib import Path
from isomap.core.exporter import ExportEngine

def test_export_pangaea(tmp_path):
    df = pd.DataFrame({
        "Site": ["A", "B"],
        "Lat": [10.0, 20.0],
        "Age": [1000, 2000]
    })
    mappings = {"SiteName": "Site", "Latitude": "Lat", "Age": "Age"}
    exporter = ExportEngine()
    out_file = tmp_path / "test_pangaea.txt"
    
    result_path = exporter.export_pangaea(df, str(out_file), mappings)
    assert Path(result_path).exists()
    
    with open(result_path, 'r') as f:
        content = f.read()
        assert "/* PANGAEA Data Submission */" in content
        assert "PI_NAME: [INSERT_PI_NAME]" in content
        assert "SiteName\tLatitude\tAge" in content
        assert "A\t10.0\t1000" in content

def test_export_noaa(tmp_path):
    df = pd.DataFrame({
        "Site": ["A", "B"],
        "Lat": [10.0, 20.0],
        "Age": [1000, 2000]
    })
    mappings = {"SiteName": "Site", "Latitude": "Lat", "Age": "Age"}
    exporter = ExportEngine()
    out_file = tmp_path / "test_noaa.xlsx"
    
    result_path = exporter.export_noaa(df, str(out_file), mappings)
    assert Path(result_path).exists()
    
    # Read the excel back
    meta_df = pd.read_excel(result_path, sheet_name='Metadata')
    assert "Investigator" in meta_df["Field"].values
    
    data_df = pd.read_excel(result_path, sheet_name='Data')
    assert "SiteName" in data_df.columns
    assert "A" in data_df["SiteName"].values
