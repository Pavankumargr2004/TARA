"""
Unit tests for the deterministic ISO/SAE 21434 risk engine.
100% assertion coverage across all scoring tables.
"""
from app.core.risk_engine import (
    calculate_attack_potential,
    calculate_impact,
    impact_label_to_int,
    lookup_risk,
    parse_selectbox_value,
)


# ---- Attack Potential (Feasibility) ----

def test_attack_potential_high():
    assert calculate_attack_potential(0, 0, 0, 0, 0) == "High"   # 0 pts
    assert calculate_attack_potential(1, 3, 3, 1, 0) == "High"   # 8 pts
    assert calculate_attack_potential(4, 3, 0, 1, 0) == "High"   # 8 pts
    assert calculate_attack_potential(0, 0, 0, 0, 4) == "High"   # 4 pts


def test_attack_potential_medium():
    assert calculate_attack_potential(4, 3, 3, 1, 0) == "Medium"  # 11 pts
    assert calculate_attack_potential(1, 3, 3, 4, 0) == "Medium"  # 11 pts
    assert calculate_attack_potential(10, 0, 0, 0, 0) == "Medium" # 10 pts
    assert calculate_attack_potential(4, 6, 3, 0, 0) == "Medium"  # 13 pts


def test_attack_potential_low():
    assert calculate_attack_potential(4, 6, 3, 1, 0) == "Low"    # 14 pts
    assert calculate_attack_potential(10, 3, 3, 1, 0) == "Low"   # 17 pts
    assert calculate_attack_potential(4, 8, 3, 4, 0) == "Low"    # 19 pts


def test_attack_potential_very_low():
    assert calculate_attack_potential(10, 8, 3, 0, 0) == "Very Low"  # 21 pts
    assert calculate_attack_potential(10, 8, 11, 10, 7) == "Very Low" # 46 pts


# ---- Impact ----

def test_impact_max():
    assert calculate_impact(4, 2, 1, 1) == 4
    assert calculate_impact(1, 3, 2, 1) == 3
    assert calculate_impact(1, 1, 1, 1) == 1
    assert calculate_impact(2, 2, 2, 2) == 2


def test_impact_label_to_int():
    assert impact_label_to_int("Severe") == 4
    assert impact_label_to_int("Major") == 3
    assert impact_label_to_int("Moderate") == 2
    assert impact_label_to_int("Negligible") == 1
    assert impact_label_to_int("Unknown") == 1  # fallback


# ---- Risk Matrix Lookup ----

def test_lookup_risk_severe():
    assert lookup_risk(4, "Very Low") == 2
    assert lookup_risk(4, "Low") == 3
    assert lookup_risk(4, "Medium") == 4
    assert lookup_risk(4, "High") == 5


def test_lookup_risk_major():
    assert lookup_risk(3, "Very Low") == 2
    assert lookup_risk(3, "Low") == 3
    assert lookup_risk(3, "Medium") == 4
    assert lookup_risk(3, "High") == 4


def test_lookup_risk_moderate():
    assert lookup_risk(2, "Very Low") == 1
    assert lookup_risk(2, "Low") == 2
    assert lookup_risk(2, "Medium") == 3
    assert lookup_risk(2, "High") == 3


def test_lookup_risk_negligible():
    assert lookup_risk(1, "Very Low") == 1
    assert lookup_risk(1, "Low") == 1
    assert lookup_risk(1, "Medium") == 1
    assert lookup_risk(1, "High") == 1


# ---- Selectbox Parser ----

def test_parse_selectbox_value():
    assert parse_selectbox_value("< 1 Month (0)") == 0
    assert parse_selectbox_value("<= 3 Months (1)") == 1
    assert parse_selectbox_value("Expert (6)") == 6
    assert parse_selectbox_value("Strictly Confidential (11)") == 11
    assert parse_selectbox_value("Bespoke (7)") == 7
