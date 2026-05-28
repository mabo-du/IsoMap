import pytest
import pandas as pd
import json
from pathlib import Path
from isomap.core.validator import ValidationEngine

def test_validation_engine(tmp_path):
    # Setup dummy schema
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    
    with open(schema_dir / "neotoma.json", "w") as f:
        json.dump({
            "required": ["Latitude"],
            "properties": {
                "Latitude": {
                    "type": "number",
                    "minimum": -90,
                    "maximum": 90
                },
                "SiteName": {
                    "type": "string"
                },
                "Age": {
                    "type": "integer",
                    "minimum": 0
                }
            }
        }, f)
        
    engine = ValidationEngine(schema_dir=str(schema_dir))
    
    # Dirty data
    df = pd.DataFrame({
        "lat_col": [45.1, 95.0, -100.0, None], # 95 and -100 are out of bounds, None violates required
        "name_col": ["Site A", "Site B", "Site C", "Site D"],
        "age_col": [1000, -500, 2000, 3000] # -500 is out of bounds
    })
    
    # Intentionally mapping bad data
    applied_mappings = {
        "Latitude": "lat_col",
        "SiteName": "name_col",
        "Age": "age_col"
    }
    
    report = engine.validate(df, "neotoma", applied_mappings)
    
    assert report["valid"] is False
    assert len(report["errors"]) > 0
    
    # Row errors check
    assert 1 in report["row_errors"] # Index 1 has lat_col = 95.0, age_col = -500
    assert 2 in report["row_errors"] # Index 2 has lat_col = -100.0
    assert 3 in report["row_errors"] # Index 3 has None for required Latitude

    # Clean data
    df_clean = pd.DataFrame({
        "lat_col": [45.1, 89.0],
        "name_col": ["Site A", "Site B"],
        "age_col": [1000, 500]
    })
    
    report_clean = engine.validate(df_clean, "neotoma", applied_mappings)
    assert report_clean["valid"] is True
    assert len(report_clean["errors"]) == 0
