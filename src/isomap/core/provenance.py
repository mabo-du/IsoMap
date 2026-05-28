"""provenance.py — Provenance tracking and Frictionless Data export.
exports: ProvenanceTracker class
used_by: main.py -> ProvenanceTracker
rules:
Must generate an audit log capturing input metadata, applied mappings, and transformations.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

class ProvenanceTracker:
    def __init__(self, dataset_name: str, input_file_path: str):
        self.dataset_name = dataset_name
        self.input_file_path = input_file_path
        self.log_entries: List[Dict[str, Any]] = []
        self._record_init()
        
    def _get_file_hash(self, file_path: str) -> str:
        """Computes SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except FileNotFoundError:
            return "file_not_found"
            
    def _record_init(self):
        """Records the initialisation of the provenance tracking."""
        file_hash = self._get_file_hash(self.input_file_path)
        self.log_entries.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "import",
            "details": {
                "dataset_name": self.dataset_name,
                "input_file": self.input_file_path,
                "sha256_hash": file_hash
            }
        })
        
    def record_mapping(self, source_column: str, target_schema_field: str, confidence_score: float, method: str):
        """Records a column mapping event."""
        self.log_entries.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "column_mapping",
            "details": {
                "source": source_column,
                "target": target_schema_field,
                "confidence": confidence_score,
                "method": method
            }
        })
        
    def record_chronology_normalisation(self, source_column: str, source_format: str, target_format: str):
        """Records a chronology normalisation event."""
        self.log_entries.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "chronology_normalisation",
            "details": {
                "column": source_column,
                "from_format": source_format,
                "to_format": target_format
            }
        })

    def record_validation(self, schema_name: str, is_valid: bool, error_count: int):
        """Records validation execution."""
        self.log_entries.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "validation",
            "details": {
                "schema": schema_name,
                "is_valid": is_valid,
                "error_count": error_count
            }
        })

    def record_export(self, output_file_path: str, format: str):
        """Records the final export."""
        self.log_entries.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "export",
            "details": {
                "output_file": output_file_path,
                "format": format
            }
        })

    def generate_frictionless_package(self, output_dir: str):
        """Generates a datapackage.json with the provenance pipeline included."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        datapackage = {
            "profile": "data-package",
            "name": self.dataset_name,
            "provenance": {
                "software": "IsoMap v1.0",
                "pipeline": self.log_entries
            }
        }
        
        with open(output_path / "datapackage.json", "w") as f:
            json.dump(datapackage, f, indent=2)
            
        return str(output_path / "datapackage.json")
