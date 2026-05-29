"""exporter.py — Core logic for converting mapped datasets to output formats.
exports: ExportEngine class
used_by: main.py -> ExportEngine
rules:
Must handle CSV, Excel, GeoJSON (Neotoma), and JSON (IsoArcH).
"""

import os
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

    def export_lipd(self, df: pd.DataFrame, output_path: str, applied_mappings: Dict[str, str], dataset_name: str = "IsoMap_Export"):
        """
        Exports the mapped dataframe to a Linked Paleo Data (LiPD) .lpd archive.
        Utilises bagit and JSON-LD packaging.
        """
        import zipfile
        import tempfile
        import shutil
        from pathlib import Path
        import bagit

        mapped_df = self._prepare_mapped_dataframe(df, applied_mappings)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write CSV
            csv_filename = f"{dataset_name}.csv"
            csv_path = temp_path / csv_filename
            mapped_df.to_csv(csv_path, index=False)
            
            # Write JSON-LD
            # Constructing a minimal, flat LiPD schema based on the mapped dataframe
            lipd_jsonld = {
                "@context": "https://linkedearth.github.io/lipd-ontology/context.jsonld",
                "@id": dataset_name,
                "dataSetName": dataset_name,
                "paleoData": [
                    {
                        "paleoDataName": "IsoMap_Export_Table",
                        "measurementTable": [
                            {
                                "measurementTableName": "Table1",
                                "filename": csv_filename,
                                "columns": [
                                    {
                                        "variableName": col,
                                        "number": i + 1,
                                        "datatype": str(mapped_df[col].dtype)
                                    } for i, col in enumerate(mapped_df.columns)
                                ]
                            }
                        ]
                    }
                ]
            }
            
            jsonld_path = temp_path / f"{dataset_name}.jsonld"
            with open(jsonld_path, "w") as f:
                json.dump(lipd_jsonld, f, indent=2)
                
            # Create bag
            bagit.make_bag(str(temp_path), {'Contact-Name': 'IsoMap Export Engine'})
            
            # Zip it up as an .lpd file
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, temp_path))
                        
        return output_path

    def export_pangaea(self, df: pd.DataFrame, output_path: str, applied_mappings: Dict[str, str]):
        """
        Exports data into a tab-delimited text file compliant with the PANGAEA format.
        Includes a boilerplate metadata header block.
        """
        mapped_df = self._prepare_mapped_dataframe(df, applied_mappings)
        
        metadata_header = (
            "/* PANGAEA Data Submission */\n"
            "CITATION: [INSERT_CITATION]\n"
            "REFERENCE: [INSERT_REFERENCE]\n"
            "PROJECT: [INSERT_PROJECT]\n"
            "PI_NAME: [INSERT_PI_NAME]\n"
            "METHOD: [INSERT_METHOD]\n"
            "/* Data */\n"
        )
        
        # Write header then data
        with open(output_path, 'w') as f:
            f.write(metadata_header)
            
        # Append dataframe as tab-delimited
        mapped_df.to_csv(output_path, sep='\t', index=False, mode='a')
        
        return output_path

    def export_noaa(self, df: pd.DataFrame, output_path: str, applied_mappings: Dict[str, str]):
        """
        Exports data into an Excel workbook compliant with the NOAA NCEI Paleoclimatology template.
        Generates a 'Metadata' sheet and a 'Data' sheet.
        """
        mapped_df = self._prepare_mapped_dataframe(df, applied_mappings)
        
        # Create a blank metadata stub
        metadata_df = pd.DataFrame([
            ["Investigator", "[INSERT_INVESTIGATOR]"],
            ["Study Name", "[INSERT_STUDY_NAME]"],
            ["Site Name", "[INSERT_SITE_NAME]"],
            ["Location", "[INSERT_LOCATION_COORDINATES]"],
            ["Publication", "[INSERT_PUBLICATION]"],
            ["Description", "[INSERT_DESCRIPTION]"]
        ], columns=["Field", "Value"])
        
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            mapped_df.to_excel(writer, sheet_name='Data', index=False)
            
        return output_path

    def export_rocrate(self, df: pd.DataFrame, output_path: str, applied_mappings: Dict[str, str]):
        """
        Exports to a Semantic Web RO-Crate containing the dataset and Frictionless datapackage.json.
        """
        from rocrate.rocrate import ROCrate
        import tempfile
        import shutil
        import os
        from pathlib import Path

        mapped_df = self._prepare_mapped_dataframe(df, applied_mappings)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write CSV
            csv_filename = "dataset.csv"
            csv_path = temp_path / csv_filename
            mapped_df.to_csv(csv_path, index=False)
            
            # Write Frictionless datapackage.json
            datapackage = {
                "profile": "tabular-data-package",
                "resources": [
                    {
                        "name": "dataset",
                        "path": csv_filename,
                        "profile": "tabular-data-resource",
                        "schema": {
                            "fields": [{"name": col, "type": "string"} for col in mapped_df.columns]
                        }
                    }
                ]
            }
            with open(temp_path / "datapackage.json", "w") as f:
                json.dump(datapackage, f, indent=2)
                
            # Build RO-Crate
            crate = ROCrate()
            
            # Add Dataset
            dataset_file = crate.add_file(str(csv_path), dest_path=csv_filename)
            dataset_file["encodingFormat"] = "text/csv"
            
            # Add datapackage.json
            dp_file = crate.add_file(str(temp_path / "datapackage.json"), dest_path="datapackage.json")
            dp_file["encodingFormat"] = "application/json"
            dp_file["about"] = {"@id": dataset_file.id}
            
            # Write RO-Crate
            crate_dir = temp_path / "rocrate"
            crate.write(str(crate_dir))
            
            # Zip it up
            import zipfile
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(crate_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, crate_dir))
                        
        return output_path
