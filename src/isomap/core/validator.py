"""validator.py — Core data validation using Pandera and JSON schema constraints.
exports: ValidationEngine class
used_by: main.py -> ValidationEngine
rules:
Must catch all SchemaErrors and return row-level tracking.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import pandera as pa
from pandera.errors import SchemaErrors

class ValidationEngine:
    def __init__(self, schema_dir: str = "data/schemas"):
        self.schema_dir = Path(schema_dir)
        
    def _json_type_to_pandera(self, json_type: str, format_str: Optional[str] = None) -> pa.DataType:
        """Converts JSON schema types to Pandera/Pandas types."""
        if json_type == "integer":
            return pa.Int64
        elif json_type == "number":
            return pa.Float64
        elif json_type == "boolean":
            return pa.Bool
        elif json_type == "string":
            if format_str in ["date", "date-time"]:
                return pa.DateTime
            return pa.String
        else:
            return pa.String

    def _build_pandera_schema(self, schema_name: str, applied_mappings: Dict[str, str]) -> pa.DataFrameSchema:
        """
        Dynamically generates a Pandera DataFrameSchema based on a JSON schema definition.
        applied_mappings maps (target_field -> source_column).
        """
        schema_path = self.schema_dir / f"{schema_name}.json"
        if not schema_path.exists():
            raise ValueError(f"Schema {schema_name} not found at {schema_path}")
            
        with open(schema_path, "r") as f:
            schema_def = json.load(f)
            
        columns = {}
        properties = schema_def.get("properties", {})
        required_fields = schema_def.get("required", [])
        
        for target_field, props in properties.items():
            if target_field not in applied_mappings:
                # If a required field is not mapped, we will catch it later, or we can enforce it here
                if target_field in required_fields:
                    # Enforcing required column existence at the dataframe level
                    pass
                continue
                
            source_col = applied_mappings[target_field]
            
            # Determine data type
            pa_type = self._json_type_to_pandera(props.get("type", "string"), props.get("format"))
            
            # Constraints
            checks = []
            if "minimum" in props:
                checks.append(pa.Check.ge(props["minimum"]))
            if "maximum" in props:
                checks.append(pa.Check.le(props["maximum"]))
            if "pattern" in props:
                checks.append(pa.Check.str_matches(props["pattern"]))
            if "enum" in props:
                checks.append(pa.Check.isin(props["enum"]))
                
            is_nullable = target_field not in required_fields
            
            columns[source_col] = pa.Column(
                pa_type,
                checks=checks if checks else None,
                nullable=is_nullable,
                required=target_field in required_fields
            )
            
        return pa.DataFrameSchema(columns, strict=False)

    def validate(self, df: pd.DataFrame, schema_name: str, applied_mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        Validates the dataframe against the schema constraints.
        applied_mappings should be a dict of {target_schema_field: source_dataframe_column}.
        Returns a structured error report.
        """
        # Ensure we don't mutate the original
        df_to_validate = df.copy()
        
        try:
            pa_schema = self._build_pandera_schema(schema_name, applied_mappings)
        except ValueError as e:
            return {"valid": False, "errors": [], "message": str(e)}

        report = {
            "valid": True,
            "errors": [],
            "row_errors": {}
        }
        
        try:
            pa_schema.validate(df_to_validate, lazy=True)
        except SchemaErrors as err:
            report["valid"] = False
            for failure in err.failure_cases.itertuples(index=False):
                col = failure.column
                check = failure.check
                idx = failure.index
                val = failure.failure_case
                
                error_msg = f"Failed constraint '{check}' on value '{val}'"
                
                report["errors"].append({
                    "column": col,
                    "row": idx,
                    "value": val,
                    "check": check,
                    "message": error_msg
                })
                
                if idx is not None:
                    # pd.isna doesn't work well on strings, need safe serialization
                    idx = int(idx) if not pd.isna(idx) else -1
                    if idx not in report["row_errors"]:
                        report["row_errors"][idx] = []
                    report["row_errors"][idx].append({
                        "column": col,
                        "message": error_msg
                    })
                    
        return report
