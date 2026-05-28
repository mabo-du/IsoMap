import pandas as pd
import numpy as np
from isomap.matching.distribution import infer_column_types

def test_infer_latitude():
    df = pd.DataFrame({"Site Lat": [45.1, 46.2, 47.3]})
    res = infer_column_types(df)
    assert res["Site Lat"]["type"] == "latitude"

def test_infer_d13c():
    df = pd.DataFrame({"unknown_col": [-21.5, -20.1, -25.4]})
    res = infer_column_types(df)
    assert res["unknown_col"]["type"] == "d13C"

def test_infer_14c():
    df = pd.DataFrame({"Date": [2500, 2650, 4500, 12000]})
    res = infer_column_types(df)
    assert res["Date"]["type"] == "14C BP"

def test_infer_lab_code():
    df = pd.DataFrame({"ID": ["OxA-12345", "UGAMS-9876", "Beta-1111"]})
    res = infer_column_types(df)
    assert res["ID"]["type"] == "lab_code"

def test_infer_taxon():
    df = pd.DataFrame({"Species": ["Bos taurus", "Homo sapiens", "Canis lupus"]})
    res = infer_column_types(df)
    assert res["Species"]["type"] == "taxon_name"
