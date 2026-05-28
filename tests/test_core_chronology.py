import pytest
from isomap.core.chronology import detect_age_format, parse_age_string, normalise_age

def test_detect_age_format():
    assert detect_age_format("Age (14C BP)") == "14C_BP"
    assert detect_age_format("cal BP") == "cal_BP"
    assert detect_age_format("Year (CE)") == "CE"
    assert detect_age_format("Age (ka)") == "ka"
    assert detect_age_format("Age (Ma)") == "Ma"
    assert detect_age_format("depth") == "unknown"

def test_parse_age_string():
    assert parse_age_string(1000) == 1000.0
    assert parse_age_string("1000") == 1000.0
    assert parse_age_string("~1000") == 1000.0
    assert parse_age_string(">1000.5") == 1000.5
    assert parse_age_string("2000 ± 50") == 2000.0
    assert parse_age_string("-500") == -500.0
    assert parse_age_string("unknown") is None
    assert parse_age_string(None) is None

def test_normalise_age():
    # cal BP -> cal BP
    assert normalise_age(1000, "cal_BP", "cal_BP") == 1000.0
    
    # CE -> cal BP (1950 anchor)
    # 2000 CE is -50 cal BP
    assert normalise_age(2000, "CE", "cal_BP") == -50.0
    # 1000 CE is 950 cal BP
    assert normalise_age(1000, "CE", "cal_BP") == 950.0
    
    # BCE -> cal BP
    # 1000 BCE (-1000 CE) is 2950 cal BP
    assert normalise_age(1000, "BCE", "cal_BP") == 2950.0
    
    # cal BP -> CE
    # 0 cal BP -> 1950 CE
    assert normalise_age(0, "cal_BP", "CE") == 1950.0
    # 1000 cal BP -> 950 CE
    assert normalise_age(1000, "cal_BP", "CE") == 950.0
    
    # ka -> cal BP
    assert normalise_age(1.5, "ka", "cal_BP") == 1500.0
    # Ma -> cal BP
    assert normalise_age(2.5, "Ma", "cal_BP") == 2500000.0
