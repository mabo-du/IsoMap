"""main.py — JSON-RPC server for Tauri IPC.
exports: run_server()
"""

import sys
import json
import traceback
from typing import Dict, Any
from isomap.core.importer import read_dataset, get_sheet_names
from isomap.matching.distribution import infer_column_types
from isomap.core.mapper import ColumnMapper

# Global instances
mapper = ColumnMapper()

def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    try:
        if method == "get_sheet_names":
            sheets = get_sheet_names(params["file_path"])
            result = {"sheets": sheets}
        elif method == "import_dataset":
            df = read_dataset(params["file_path"], params.get("sheet_name"))
            
            # For preview, just send the first 50 rows
            preview_df = df.head(50)
            
            # Infer column types
            inferred_types = infer_column_types(df)
            
            # Convert to JSON serializable formats
            # Replace NaNs with None for JSON
            preview_data = preview_df.replace({float('nan'): None}).to_dict(orient="records")
            
            result = {
                "columns": list(df.columns),
                "preview": preview_data,
                "inferred_types": inferred_types,
                "total_rows": len(df)
            }
        elif method == "map_columns":
            df = read_dataset(params["file_path"], params.get("sheet_name"))
            mappings = mapper.map_columns(df, params["schema_name"])
            result = {"mappings": mappings}
        elif method == "save_override":
            mapper.save_override(params["source_column"], params["target_field"], params["schema_name"])
            result = {"success": True}
        else:
            raise ValueError(f"Unknown method: {method}")

        return {"jsonrpc": "2.0", "result": result, "id": request_id}
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": str(e), "data": traceback.format_exc()},
            "id": request_id
        }

def run_server():
    """Reads JSON-RPC requests from stdin and writes responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            err = {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}
            print(json.dumps(err), flush=True)
        except Exception as e:
            err = {"jsonrpc": "2.0", "error": {"code": -32603, "message": "Internal error"}, "id": None}
            print(json.dumps(err), flush=True)

if __name__ == "__main__":
    run_server()
