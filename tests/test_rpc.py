"""test_rpc.py — Tests JSON-RPC handlers for main.py."""
import json
import pytest
from isomap.main import handle_request

def test_invalid_request():
    response = handle_request("not a dict")
    assert response["error"]["code"] == -32600

def test_unknown_method():
    response = handle_request({"method": "not_real", "id": 1})
    assert response["error"]["code"] == -32000
    assert "Unknown method" in response["error"]["message"]

def test_get_sheet_names():
    req = {
        "method": "get_sheet_names",
        "params": {"file_path": "tests/test_data/legacy_data.csv"},
        "id": 2
    }
    response = handle_request(req)
    assert response["id"] == 2
    assert "sheets" in response["result"]
    assert response["result"]["sheets"] == []

def test_import_dataset():
    req = {
        "method": "import_dataset",
        "params": {"file_path": "tests/test_data/legacy_data.csv"},
        "id": 3
    }
    response = handle_request(req)
    assert response["id"] == 3
    assert "columns" in response["result"]
    assert "preview" in response["result"]
    assert "total_rows" in response["result"]
