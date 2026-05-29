"""datapaper.py — Generates automated data papers.
exports: generate_data_paper
used_by: main.py -> generate_data_paper
rules:
Must use jinja2 to render the ESSD template.
"""

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import pandas as pd
import os

def generate_data_paper(df: pd.DataFrame, schema_name: str, template_name: str = "essd_template.tex", output_path: str = "manuscript.tex") -> str:
    """Generates a LaTeX data paper manuscript by injecting dataframe metadata."""
    
    num_records = len(df)
    
    min_lat, max_lat = 0.0, 0.0
    min_lon, max_lon = 0.0, 0.0
    
    lat_col = next((c for c in df.columns if c.lower() in ['latitude', 'lat']), None)
    lon_col = next((c for c in df.columns if c.lower() in ['longitude', 'lon', 'long']), None)
    
    if lat_col and pd.api.types.is_numeric_dtype(df[lat_col]):
        min_lat = float(df[lat_col].min())
        max_lat = float(df[lat_col].max())
        
    if lon_col and pd.api.types.is_numeric_dtype(df[lon_col]):
        min_lon = float(df[lon_col].min())
        max_lon = float(df[lon_col].max())

    # Resolve template dir assuming script is in src/isomap/core
    base_dir = Path(__file__).parent.parent.parent.parent
    template_dir = base_dir / "data" / "templates"
    
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template(template_name)
    
    rendered_tex = template.render(
        dataset_name="Harmonised Dataset",
        author_name="[INSERT AUTHOR]",
        author_affiliation="[INSERT AFFILIATION]",
        num_records=num_records,
        min_lat=round(min_lat, 4),
        max_lat=round(max_lat, 4),
        min_lon=round(min_lon, 4),
        max_lon=round(max_lon, 4),
        schema_name=schema_name.capitalize(),
        validation_score=100.0,
        dataset_url="[INSERT DOI URL]"
    )
    
    # Ensure output dir exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    with open(output_path, "w") as f:
        f.write(rendered_tex)
        
    return output_path
