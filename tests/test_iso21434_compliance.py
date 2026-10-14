"""
Unit tests validating strict ISO/SAE 21434 and UNECE R155 standard compliance:
- Clause 15.6 Attack Potential Calculation & Feasibility Mapping
- Clause 15.5 Impact Rating Matrix (Safety, Financial, Operational, Privacy)
- Clause 15.7 Annex H Risk Level Matrix Determination (1 to 5)
"""
import pytest
from app.core.risk_engine import (
    calculate_attack_potential,
    calculate_impact,
    impact_label_to_int,
    lookup_risk,
    RISK_MATRIX,
    IMPACT_LABEL_MAP
)


def test_iso21434_attack_potential_thresholds():
    # <= 9 -> High
    assert calculate_attack_potential(0, 3, 0, 1, 0) == "High"  # total 4
    assert calculate_attack_potential(1, 3, 3, 1, 1) == "High"  # total 9

    # 10 - 13 -> Medium
    assert calculate_attack_potential(1, 3, 3, 1, 2) == "Medium"  # total 10
    assert calculate_attack_potential(4, 3, 3, 1, 2) == "Medium"  # total 13

    # 14 - 19 -> Low
    assert calculate_attack_potential(4, 3, 3, 4, 0) == "Low"  # total 14
    assert calculate_attack_potential(10, 3, 3, 1, 2) == "Low"  # total 19

    # >= 20 -> Very Low
    assert calculate_attack_potential(10, 6, 3, 1, 0) == "Very Low"  # total 20
    assert calculate_attack_potential(10, 8, 11, 10, 7) == "Very Low"  # total 46


def test_iso21434_impact_aggregation():
    # Maximum impact dimension governs the overall impact score
    assert calculate_impact(safety=4, financial=1, operational=2, privacy=1) == 4
    assert calculate_impact(safety=1, financial=3, operational=2, privacy=1) == 3
    assert calculate_impact(safety=1, financial=1, operational=1, privacy=2) == 2
    assert calculate_impact(safety=1, financial=1, operational=1, privacy=1) == 1


def test_impact_label_to_int_mapping():
    assert impact_label_to_int("Severe") == 4
    assert impact_label_to_int("Major") == 3
    assert impact_label_to_int("Moderate") == 2
    assert impact_label_to_int("Negligible") == 1
    assert impact_label_to_int("UnknownLabel") == 1


def test_iso21434_risk_matrix_full_coverage():
    # Test all 16 cells of the standard ISO/SAE 21434 Annex H matrix
    expected_matrix = {
        4: {"Very Low": 2, "Low": 3, "Medium": 4, "High": 5},
        3: {"Very Low": 2, "Low": 3, "Medium": 4, "High": 4},
        2: {"Very Low": 1, "Low": 2, "Medium": 3, "High": 3},
        1: {"Very Low": 1, "Low": 1, "Medium": 1, "High": 1},
    }
    for impact, feasibilities in expected_matrix.items():
        for feas, expected_risk in feasibilities.items():
            assert lookup_risk(impact, feas) == expected_risk


def test_iso21434_safety_critical_hazard():
    # Severe safety impact (ASIL-D) with High feasibility must yield maximum Risk Level 5
    safety_impact = impact_label_to_int("Severe")
    feasibility = calculate_attack_potential(0, 0, 0, 0, 0)  # High
    risk = lookup_risk(safety_impact, feasibility)
    assert risk == 5
