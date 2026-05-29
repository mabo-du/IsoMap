"""main.py — JSON-RPC server for Tauri IPC.
exports: run_server()
"""

import sys
import json
import traceback
from typing import Dict, Any
import json as json_lib
from isomap.core.importer import read_dataset, get_sheet_names
from isomap.matching.distribution import infer_column_types
from isomap.core.mapper import ColumnMapper
from isomap.core.spatial import to_geodataframe, get_bounding_box
from isomap.core.validator import ValidationEngine
from isomap.core.exporter import ExportEngine
from isomap.core.chronology import process_chronology_dataframe

# Global instances
mapper = ColumnMapper()
validator = ValidationEngine()
exporter = ExportEngine()

def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict) or "method" not in request:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": "Invalid Request"},
            "id": request.get("id") if isinstance(request, dict) else None
        }

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
        elif method == "get_spatial_preview":
            df = read_dataset(params["file_path"], params.get("sheet_name"))
            gdf = to_geodataframe(df, params["lat_col"], params["lon_col"])
            geojson = gdf.to_json()
            bbox = get_bounding_box(gdf)
            result = {
                "geojson": json_lib.loads(geojson),
                "bbox": bbox
            }
        elif method == "validate_dataset":
            df = read_dataset(params["file_path"], params.get("sheet_name"))
            report = validator.validate(df, params["schema_name"], params["applied_mappings"])
            result = {"report": report}
        elif method == "export_dataset":
            df = read_dataset(params["file_path"], params.get("sheet_name"))
            fmt = params.get("format", "csv")
            out_path = params["output_path"]
            mappings = params["applied_mappings"]
            
            if fmt == "csv":
                exporter.export_csv(df, out_path, mappings)
            elif fmt == "xlsx":
                exporter.export_excel(df, out_path, mappings)
            elif fmt == "geojson":
                # Assuming Latitude/Longitude are the exact target fields in the schema
                exporter.export_geojson(df, out_path, mappings, lat_field="Latitude", lon_field="Longitude")
            elif fmt == "isoarch_json":
                exporter.export_isoarch_json(df, out_path, mappings)
            elif fmt == "lipd":
                dataset_name = params.get("dataset_name", "IsoMap_Export")
                exporter.export_lipd(df, out_path, mappings, dataset_name)
            elif fmt == "pangaea":
                exporter.export_pangaea(df, out_path, mappings)
            elif fmt == "noaa":
                exporter.export_noaa(df, out_path, mappings)
            elif fmt == "rocrate":
                exporter.export_rocrate(df, out_path, mappings)
            else:
                raise ValueError(f"Unknown format: {fmt}")
                
            result = {"success": True, "output_path": out_path}
        elif method == "generate_data_paper":
            from isomap.core.datapaper import generate_data_paper
            df = read_dataset(params["file_path"], params.get("sheet_name"))
            out_path = params["output_path"]
            generate_data_paper(df, params["schema_name"], output_path=out_path)
            result = {"success": True, "output_path": out_path}
        elif method == "normalise_chronology":
            df = read_dataset(params["file_path"], params.get("sheet_name"))
            mappings = params.get("mappings", {}) # Dict[str, Tuple[str, str]]
            norm_df = process_chronology_dataframe(df, mappings)
            
            # For preview purposes, return the first few rows of the normalised columns
            target_cols = list(mappings.keys())
            preview_df = norm_df[target_cols].head(10)
            preview = preview_df.replace({float("nan"): None}).to_dict(orient="records")
            result = {"preview": preview}
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
