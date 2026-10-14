"""
Unit tests for Pydantic core data schemas (TrustBoundary and ThreatScenario).
"""
import pytest
from app.core.schemas import TrustBoundary, ThreatScenario


def test_trust_boundary_schema():
    tb = TrustBoundary(
        boundary_id="TB-01",
        source_domain="External Cloud",
        target_domain="Telematics Gateway",
        interface_type="Cellular 5G",
        exposure_level="High"
    )
    assert tb.boundary_id == "TB-01"
    assert tb.exposure_level == "High"
    dump = tb.model_dump()
    assert dump["source_domain"] == "External Cloud"


def test_threat_scenario_defaults():
    threat = ThreatScenario(
        threat_id="THR-001",
        target_asset="Braking ECU",
        trust_boundary_id="TB-02",
        stride_category="Tampering",
        mitre_attack_id="T1565",
        threat_description="Unauthorized CAN bus brake actuation command injection",
        attack_path=["Cellular", "TCU", "Gateway", "Brake ECU"],
        cybersecurity_requirement="CSR-BRK-01: Authenticate all braking commands",
        thales_mitigation_control="Thales SecOC & Hardware Cryptographic Keys",
        citations=["ISO 21434 Annex E"],
        elapsed_time=2,
        expertise=2,
        knowledge=1,
        window=1,
        equipment=0,
        impact_safety="Severe",
        impact_financial="Moderate",
        impact_operational="Major",
        impact_privacy="Negligible"
    )
    assert threat.review_status == "Pending Review"
    assert threat.reviewer_notes == ""
    assert threat.calculated_feasibility is None
    assert threat.risk_level is None


def test_threat_scenario_serialization():
    threat = ThreatScenario(
        threat_id="THR-002",
        target_asset="Battery Management System",
        trust_boundary_id="TB-03",
        stride_category="Denial of Service",
        mitre_attack_id="T1499",
        threat_description="Overvoltage injection leading to contactor opening",
        attack_path=["Fast Charger", "EVCC", "BMS"],
        cybersecurity_requirement="CSR-BMS-01: Enforce MAC validation",
        thales_mitigation_control="Thales Luna PCIe HSM",
        citations=["ISO 15118"],
        elapsed_time=1,
        expertise=1,
        knowledge=1,
        window=2,
        equipment=1,
        impact_safety="Major",
        impact_financial="Severe",
        impact_operational="Major",
        impact_privacy="Negligible",
        calculated_feasibility="Medium",
        calculated_impact="Severe",
        risk_level=4,
        review_status="Approved",
        reviewer_notes="Verified by Lead Auditor"
    )
    data = threat.model_dump()
    assert data["threat_id"] == "THR-002"
    assert data["risk_level"] == 4
    assert data["review_status"] == "Approved"

    json_str = threat.model_dump_json()
    assert "THR-002" in json_str
    assert "Battery Management System" in json_str
