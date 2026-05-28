import pytest
import json
from pathlib import Path
from isomap.core.provenance import ProvenanceTracker

def test_provenance_tracker(tmp_path):
    # Create dummy input file
    input_file = tmp_path / "data.csv"
    input_file.write_text("dummy,data\n1,2")
    
    tracker = ProvenanceTracker(dataset_name="TestDataset", input_file_path=str(input_file))
    
    assert len(tracker.log_entries) == 1
    assert tracker.log_entries[0]["action"] == "import"
    assert tracker.log_entries[0]["details"]["dataset_name"] == "TestDataset"
    
    # Record events
    tracker.record_mapping("source_col", "Latitude", 0.95, "exact")
    tracker.record_chronology_normalisation("age", "14C_BP", "cal_BP")
    tracker.record_validation("neotoma", True, 0)
    tracker.record_export(str(tmp_path / "out.csv"), "csv")
    
    assert len(tracker.log_entries) == 5
    
    # Test export
    out_dir = tmp_path / "pkg"
    pkg_path = tracker.generate_frictionless_package(str(out_dir))
    
    assert Path(pkg_path).exists()
    
    with open(pkg_path, "r") as f:
        data = json.load(f)
        assert data["name"] == "TestDataset"
        assert len(data["provenance"]["pipeline"]) == 5
        assert data["provenance"]["software"] == "IsoMap v1.0"
