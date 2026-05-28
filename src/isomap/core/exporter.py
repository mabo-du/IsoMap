"""exporter.py — Core logic for converting mapped datasets to output formats.
exports: ExportEngine class
used_by: main.py -> ExportEngine
rules:
Must handle CSV, Excel, GeoJSON (Neotoma), and JSON (IsoArcH).
"""

import json
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
from isomap.core.spatial import to_geodataframe

class ExportEngine:
    def __init__(self):
        pass

    def _prepare_mapped_dataframe(self, df: pd.DataFrame, applied_mappings: Dict[str, str]) -> pd.DataFrame:
        """
        Creates a new DataFrame containing only the mapped columns,
        renamed to the target schema fields.
        """
        # Reverse mapping: source_col -> target_field
        rename_map = {source: target for target, source in applied_mappings.items()}
        
        # Keep only mapped columns
        cols_to_keep = list(rename_map.keys())
        # Make sure they exist in dataframe
        cols_to_keep = [c for c in cols_to_keep if c in df.columns]
        
        mapped_df = df[cols_to_keep].copy()
        mapped_df = mapped_df.rename(columns=rename_map)
        return mapped_df

    def export_csv(self, df: pd.DataFrame, output_path: str, applied_mappings: Dict[str, str]):
        """Exports the mapped dataframe to a CSV file."""
        mapped_df = self._prepare_mapped_dataframe(df, applied_mappings)
        mapped_df.to_csv(output_path, index=False)
        return output_path

    def export_excel(self, df: pd.DataFrame, output_path: str, applied_mappings: Dict[str, str]):
        """Exports the mapped dataframe to an Excel file."""
        mapped_df = self._prepare_mapped_dataframe(df, applied_mappings)
        mapped_df.to_excel(output_path, index=False)
        return output_path

    def export_geojson(self, df: pd.DataFrame, output_path: str, applied_mappings: Dict[str, str], lat_field: str = "Latitude", lon_field: str = "Longitude"):
        """
        Exports to GeoJSON format (typically for Neotoma).
        Requires target schema fields for Latitude and Longitude.
        """
        mapped_df = self._prepare_mapped_dataframe(df, applied_mappings)
        
        if lat_field not in mapped_df.columns or lon_field not in mapped_df.columns:
            raise ValueError(f"Latitude ({lat_field}) and Longitude ({lon_field}) fields are required for GeoJSON export.")
            
        gdf = to_geodataframe(mapped_df, lat_col=lat_field, lon_col=lon_field)
        gdf.to_file(output_path, driver="GeoJSON")
        return output_path

    def export_isoarch_json(self, df: pd.DataFrame, output_path: str, applied_mappings: Dict[str, str]):
        """
        Exports to a JSON array of objects format (IsoArcH REST API payload).
        """
        mapped_df = self._prepare_mapped_dataframe(df, applied_mappings)
        
        # Handle NaN values for JSON compatibility
        mapped_df = mapped_df.replace({float("nan"): None})
        
        records = mapped_df.to_dict(orient="records")
        
        with open(output_path, "w") as f:
            json.dump(records, f, indent=2)
            
        return output_path
