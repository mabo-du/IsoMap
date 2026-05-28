"""spatial.py — Geographic coordinate conversions and GeoPandas integration.
exports: parse_coordinate(coord), to_geodataframe(df, lat_col, lon_col), get_bounding_box(gdf)
used_by: main.py -> to_geodataframe
rules:
Must handle decimal degrees, DMS, and DMM formats. Default CRS is EPSG:4326.
"""

import re
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from typing import Optional, Tuple, Dict, Any, Union

def parse_coordinate(coord: Union[str, int, float]) -> Optional[float]:
    """
    Parses various geographic coordinate formats (DD, DMS, DMM) into Decimal Degrees (float).
    Returns None if parsing fails.
    """
    if pd.isna(coord) or coord == "":
        return None
        
    if isinstance(coord, (int, float)):
        return float(coord)
        
    coord = str(coord).strip().upper()
    
    parts = re.findall(r'\d+(?:\.\d+)?', coord)
    if not parts:
        return None
        
    direction = None
    dir_match = re.search(r'[NSEW]', coord)
    if dir_match:
        direction = dir_match.group(0)

    try:
        if len(parts) == 3:
            # DMS (Degrees Minutes Seconds)
            d = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            val = d + m/60.0 + s/3600.0
        elif len(parts) == 2:
            # DMM (Degrees Decimal Minutes)
            d = float(parts[0])
            m = float(parts[1])
            val = d + m/60.0
        elif len(parts) == 1:
            # DD (Decimal Degrees)
            val = float(parts[0])
        else:
            return None

        # Apply sign
        if direction in ['S', 'W']:
            val = -val
        elif '-' in coord and val > 0 and not direction:
            val = -val
            
        return val
    except ValueError:
        return None

def clean_coordinates(df: pd.DataFrame, lat_col: str, lon_col: str) -> pd.DataFrame:
    """Parses coordinate columns in a dataframe."""
    df_clean = df.copy()
    if lat_col in df_clean.columns:
        df_clean[lat_col] = df_clean[lat_col].apply(parse_coordinate)
    if lon_col in df_clean.columns:
        df_clean[lon_col] = df_clean[lon_col].apply(parse_coordinate)
    return df_clean

def to_geodataframe(df: pd.DataFrame, lat_col: str, lon_col: str, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """
    Converts a pandas DataFrame into a GeoPandas GeoDataFrame.
    Automatically parses coordinate strings and creates Point geometries.
    Drops rows where lat or lon cannot be parsed.
    """
    if lat_col not in df.columns or lon_col not in df.columns:
        raise ValueError(f"Columns {lat_col} and {lon_col} must exist in the DataFrame")
        
    df_clean = clean_coordinates(df, lat_col, lon_col)
    
    # Drop rows without valid coordinates for the spatial representation
    df_spatial = df_clean.dropna(subset=[lat_col, lon_col])
    
    geometry = [Point(xy) for xy in zip(df_spatial[lon_col], df_spatial[lat_col])]
    gdf = gpd.GeoDataFrame(df_spatial, geometry=geometry, crs=crs)
    return gdf

def get_bounding_box(gdf: gpd.GeoDataFrame) -> Optional[Dict[str, float]]:
    """
    Calculates the bounding box of a GeoDataFrame.
    Returns None if empty, else {"min_lon": float, "min_lat": float, "max_lon": float, "max_lat": float}
    """
    if gdf.empty:
        return None
        
    bounds = gdf.total_bounds # [minx, miny, maxx, maxy]
    return {
        "min_lon": float(bounds[0]),
        "min_lat": float(bounds[1]),
        "max_lon": float(bounds[2]),
        "max_lat": float(bounds[3])
    }
