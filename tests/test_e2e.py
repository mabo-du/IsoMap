"""test_e2e.py — End-to-end backend tests for the entire pipeline."""
import os
import pytest
from isomap.main import handle_request

def test_full_e2e_pipeline(tmp_path):
    """Tests importing, mapping, validation, and exporting in sequence."""
    
    # 1. Import
    import_req = {
        "method": "import_dataset",
        "params": {"file_path": "tests/test_data/legacy_data.csv"},
        "id": 1
    }
    import_res = handle_request(import_req)
    assert import_res["id"] == 1
    assert "columns" in import_res["result"]
    
    # 2. Map
    map_req = {
        "method": "map_columns",
        "params": {
            "file_path": "tests/test_data/legacy_data.csv",
            "schema_name": "neotoma_v2"
        },
        "id": 2
    }
    map_res = handle_request(map_req)
    assert map_res["id"] == 2
    mappings = map_res["result"]["mappings"]
    assert "14C BP_uncal" in mappings
    
    # 3. Validate
    # Fake applied mappings based on what was found
    applied_mappings = {
        "SiteName": "site",
        "Latitude": "lat",
        "Longitude": "lon",
        "Age": "age"
    }
    
    val_req = {
        "method": "validate_dataset",
        "params": {
            "file_path": "tests/test_data/legacy_data.csv",
            "schema_name": "neotoma_v2",
            "applied_mappings": applied_mappings
        },
        "id": 3
    }
    val_res = handle_request(val_req)
    assert val_res["id"] == 3
    assert "report" in val_res["result"]
    
    # 4. Export RO-Crate
    export_path = str(tmp_path / "rocrate.zip")
    exp_req = {
        "method": "export_dataset",
        "params": {
            "file_path": "tests/test_data/legacy_data.csv",
            "schema_name": "neotoma_v2",
            "applied_mappings": applied_mappings,
            "format": "rocrate",
            "output_path": export_path
        },
        "id": 4
    }
    exp_res = handle_request(exp_req)
    assert exp_res["id"] == 4
    assert os.path.exists(export_path)
