import pytest
import pandas as pd
from isomap.core.spatial import parse_coordinate, to_geodataframe, get_bounding_box

def test_parse_coordinate_dd():
    assert parse_coordinate(45.123) == 45.123
    assert parse_coordinate("45.123") == 45.123
    assert parse_coordinate("45.123 N") == 45.123
    assert parse_coordinate("45.123 S") == -45.123
    assert parse_coordinate("120.45 W") == -120.45
    assert parse_coordinate("-120.45") == -120.45

def test_parse_coordinate_dms():
    # 45°15'30" = 45 + 15/60 + 30/3600 = 45.258333
    res = parse_coordinate("45°15'30\"N")
    assert abs(res - 45.258333) < 1e-5
    
    # -45°15'30"
    res = parse_coordinate("45°15'30\"S")
    assert abs(res - (-45.258333)) < 1e-5

def test_parse_coordinate_dmm():
    # 45°15.5' = 45 + 15.5/60 = 45.258333
    res = parse_coordinate("45°15.5'N")
    assert abs(res - 45.258333) < 1e-5

def test_parse_coordinate_invalid():
    assert parse_coordinate("") is None
    assert parse_coordinate(None) is None
    assert parse_coordinate("Invalid_String") is None

def test_to_geodataframe():
    df = pd.DataFrame({
        "site": ["A", "B", "C"],
        "lat": ["45 N", "46 S", "invalid"],
        "lon": ["120 W", "110 E", "100 W"]
    })
    
    gdf = to_geodataframe(df, "lat", "lon")
    
    # C should be dropped
    assert len(gdf) == 2
    assert gdf.crs.to_string() == "EPSG:4326"
    
    # Point A
    assert gdf.iloc[0].geometry.y == 45.0
    assert gdf.iloc[0].geometry.x == -120.0
    
def test_bounding_box():
    df = pd.DataFrame({
        "lat": [10.0, 20.0],
        "lon": [100.0, 110.0]
    })
    gdf = to_geodataframe(df, "lat", "lon")
    bbox = get_bounding_box(gdf)
    
    assert bbox["min_lon"] == 100.0
    assert bbox["min_lat"] == 10.0
    assert bbox["max_lon"] == 110.0
    assert bbox["max_lat"] == 20.0
