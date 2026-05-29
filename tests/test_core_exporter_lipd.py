import pytest
import pandas as pd
import zipfile
import json
from pathlib import Path
from isomap.core.exporter import ExportEngine

def test_export_lipd(tmp_path):
    df = pd.DataFrame({
        "Site": ["A", "B"],
        "Lat": [10.0, 20.0],
        "Age": [1000, 2000]
    })
    
    mappings = {
        "SiteName": "Site",
        "Latitude": "Lat",
        "Age": "Age"
    }
    
    exporter = ExportEngine()
    
    out_file = tmp_path / "test.lpd"
    
    result_path = exporter.export_lipd(df, str(out_file), mappings, dataset_name="TestDataset")
    
    assert Path(result_path).exists()
    
    # Check if it's a valid zip file
    assert zipfile.is_zipfile(result_path)
    
    with zipfile.ZipFile(result_path, 'r') as z:
        files = z.namelist()
        assert "bagit.txt" in files
        assert "data/TestDataset.csv" in files
        assert "data/TestDataset.jsonld" in files
        
        # Read the JSON-LD payload to ensure columns were mapped
        with z.open("data/TestDataset.jsonld") as f:
            json_ld = json.load(f)
            
            assert json_ld["dataSetName"] == "TestDataset"
            
            # The mappings say: "SiteName", "Latitude", "Age"
            cols = json_ld["paleoData"][0]["measurementTable"][0]["columns"]
            var_names = [col["variableName"] for col in cols]
            
            assert "SiteName" in var_names
            assert "Latitude" in var_names
            assert "Age" in var_names
