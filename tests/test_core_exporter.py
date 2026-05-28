import pytest
import pandas as pd
import json
from pathlib import Path
from isomap.core.exporter import ExportEngine

def test_export_engine(tmp_path):
    engine = ExportEngine()
    
    df = pd.DataFrame({
        "source_lat": [45.1, 46.2],
        "source_lon": [12.3, 14.5],
        "source_name": ["Site A", "Site B"],
        "unmapped_col": ["ignore", "this"]
    })
    
    applied_mappings = {
        "Latitude": "source_lat",
        "Longitude": "source_lon",
        "SiteName": "source_name"
    }
    
    # Test CSV
    csv_path = tmp_path / "out.csv"
    engine.export_csv(df, str(csv_path), applied_mappings)
    
    assert csv_path.exists()
    out_df = pd.read_csv(csv_path)
    assert list(out_df.columns) == ["Latitude", "Longitude", "SiteName"]
    assert "unmapped_col" not in out_df.columns
    assert len(out_df) == 2
    
    # Test GeoJSON
    geojson_path = tmp_path / "out.geojson"
    engine.export_geojson(df, str(geojson_path), applied_mappings, lat_field="Latitude", lon_field="Longitude")
    
    assert geojson_path.exists()
    with open(geojson_path, "r") as f:
        data = json.load(f)
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2
        assert data["features"][0]["properties"]["SiteName"] == "Site A"
        assert data["features"][0]["geometry"]["coordinates"] == [12.3, 45.1]
        
    # Test IsoArcH JSON
    json_path = tmp_path / "isoarch.json"
    engine.export_isoarch_json(df, str(json_path), applied_mappings)
    
    assert json_path.exists()
    with open(json_path, "r") as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["SiteName"] == "Site A"
        assert data[0]["Latitude"] == 45.1
