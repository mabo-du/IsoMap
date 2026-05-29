import pandas as pd
import pytest
from pathlib import Path
import json

from isomap.matching.exact import normalize_string, exact_match
from isomap.matching.fuzzy import fuzzy_match
from isomap.matching.preferences import PreferenceCache
from isomap.matching.semantic import SemanticMatcher
from isomap.core.mapper import ColumnMapper

def test_normalize_string():
    assert normalize_string(" Site Name ") == "sitename"
    assert normalize_string("14C_BP_uncal") == "14cbpuncal"
    assert normalize_string("Lat.") == "lat"

def test_exact_match():
    targets = ["SiteName", "Latitude", "Longitude", "Value"]
    assert exact_match("site name", targets) == "SiteName"
    assert exact_match("Lat.", targets) is None

def test_fuzzy_match():
    targets = ["SiteName", "Latitude", "Longitude", "Value"]
    matches = fuzzy_match("site nam", targets)
    assert len(matches) > 0
    assert matches[0]["target"] == "SiteName"
    assert matches[0]["confidence"] > 0.8

def test_preference_cache(tmp_path):
    db_path = tmp_path / "prefs.db"
    cache = PreferenceCache(str(db_path))
    
    # Empty cache
    assert cache.get_preference("sitename") is None
    
    # Store and retrieve
    cache.store_preference("sitename", "SiteName", repository="neotoma")
    assert cache.get_preference("sitename", repository="neotoma") == "SiteName"
    assert cache.get_preference("sitename", repository="isoarch") is None

def test_semantic_match():
    matcher = SemanticMatcher()
    targets = ["Latitude", "Longitude", "TaxonName", "Value"]
    
    # 'species' should semantically match 'TaxonName'
    matches = matcher.match("species", targets, threshold=0.3)
    assert len(matches) > 0
    
def test_column_mapper(tmp_path):
    # Setup dummy schemas and DB
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    
    with open(schema_dir / "neotoma.json", "w") as f:
        json.dump({
            "properties": {
                "SiteName": {},
                "Latitude": {},
                "TaxonName": {},
                "Value": {}
            }
        }, f)
        
    db_path = tmp_path / "prefs.db"
    
    mapper = ColumnMapper(db_path=str(db_path), schema_dir=str(schema_dir))
    
    df = pd.DataFrame({
        "site": ["Cave A"],
        "lat": [45.1],
        "species": ["Bos taurus"],
        "d13c_value": [-21.5]
    })
    
    results = mapper.map_columns(df, "neotoma")
    
    assert "site" in results
    assert "lat" in results
    assert "species" in results
    assert "d13c_value" in results
    
    # Add an override and verify it's used
    mapper.save_override("d13c_value", "Value", "neotoma")
    results2 = mapper.map_columns(df, "neotoma")
    d13c_suggestions = results2["d13c_value"]
    
    assert any(s["target"] == "Value" and s["method"] == "preference" for s in d13c_suggestions)

def test_valentine_match():
    from isomap.matching.valentine_matcher import ValentineMatcher
    matcher = ValentineMatcher()
    targets = ["Latitude", "Longitude", "TaxonName", "Value"]
    series = pd.Series(["45.0", "46.1", "44.9"])
    matches = matcher.match("lat", series, targets)
    assert len(matches) > 0
    # Cupid / Coma Name matchers often match 'lat' and 'Latitude' 
    assert any(m["target"] == "Latitude" for m in matches)
