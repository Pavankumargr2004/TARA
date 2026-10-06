"""
Pytest unit and integration tests for Production Features:
1. OAuth2 Authentication & RBAC
2. AUTOSAR ARXML & CAN DBC Architecture Parsers
3. Jira & Jama ALM REST Synchronization Services
"""
import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.core.auth import hash_password, verify_password, create_access_token, decode_access_token, ROLES
from app.services.autosar_dbc_parser import AutosarArxmlParser, CanDbcParser
from app.services.alm_sync_service import JiraSyncService, JamaSyncService
from app.core.schemas import ThreatScenario

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. OAUTH2 & RBAC AUTHENTICATION TESTS
# -----------------------------------------------------------------------------

def test_password_hashing_and_verification():
    raw_pass = "SecurePass2026!"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPass", hashed) is False


def test_jwt_token_generation_and_decoding():
    data = {"sub": "engineer", "role": ROLES["CYBERSECURITY_ENGINEER"]}
    token = create_access_token(data, expires_in=3600)
    assert isinstance(token, str)
    assert len(token) > 20
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.get("sub") == "engineer"
    assert decoded.get("role") == ROLES["CYBERSECURITY_ENGINEER"]


def test_auth_login_api_endpoint():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "engineer", "password": "Eng@123"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert "access_token" in res_data
    assert res_data["token_type"] == "bearer"
    assert res_data["username"] == "engineer"
    assert res_data["role"] == ROLES["CYBERSECURITY_ENGINEER"]


def test_auth_me_api_endpoint():
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "Admin@123"}
    ).json()
    token = login_res["access_token"]
    
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["username"] == "admin"
    assert me_data["role"] == ROLES["SYSTEM_ARCHITECT"]


# -----------------------------------------------------------------------------
# 2. AUTOSAR ARXML & CAN DBC PARSER TESTS
# -----------------------------------------------------------------------------

def test_autosar_arxml_parser():
    with open("sample_data/zone_architecture_arxml_spec.arxml", "r", encoding="utf-8") as f:
        arxml_content = f.read()
    
    parsed = AutosarArxmlParser.parse_arxml_string(arxml_content)
    assert parsed["format"] == "AUTOSAR_ARXML"
    assert len(parsed["ecus"]) >= 3
    assert len(parsed["trust_boundaries"]) >= 2
    
    ecu_names = [e["name"] for e in parsed["ecus"]]
    assert "Zone_Controller_FrontRight" in ecu_names
    assert "Central_Compute_Cluster" in ecu_names


def test_can_dbc_parser():
    with open("sample_data/ev_powertrain_battery_spec.dbc", "r", encoding="utf-8") as f:
        dbc_content = f.read()
    
    parsed = CanDbcParser.parse_dbc_string(dbc_content)
    assert parsed["format"] == "CAN_DBC"
    assert len(parsed["ecus"]) >= 3
    assert len(parsed["messages"]) >= 3
    
    msg_names = [m["name"] for m in parsed["messages"]]
    assert "BMS_BatteryStatus" in msg_names
    assert "Inverter_TorqueRequest" in msg_names


def test_arxml_and_dbc_upload_api_endpoints():
    with open("sample_data/zone_architecture_arxml_spec.arxml", "rb") as f:
        res_arxml = client.post("/api/v1/parse/arxml", files={"file": ("test.arxml", f, "text/xml")})
    assert res_arxml.status_code == 200
    assert res_arxml.json()["status"] == "Success"

    with open("sample_data/ev_powertrain_battery_spec.dbc", "rb") as f:
        res_dbc = client.post("/api/v1/parse/dbc", files={"file": ("test.dbc", f, "text/plain")})
    assert res_dbc.status_code == 200
    assert res_dbc.json()["status"] == "Success"


# -----------------------------------------------------------------------------
# 3. JIRA & JAMA ALM REST SYNC TESTS
# -----------------------------------------------------------------------------

def test_jira_and_jama_alm_sync_service():
    test_threat = ThreatScenario(
        threat_id="THR-ALM-101",
        target_asset="BMS Control Unit",
        trust_boundary_id="TB-EV-01",
        stride_category="Tampering",
        mitre_attack_id="T1565",
        threat_description="High voltage fast charge voltage override attack",
        attack_path=["Charger", "BMS"],
        cybersecurity_requirement="CSR-BMS-01: Enforce 128-bit AES-CMAC validation",
        thales_mitigation_control="Thales SecOC & HSM",
        citations=["ISO 21434 Annex G"],
        elapsed_time=1,
        expertise=3,
        knowledge=3,
        window=1,
        equipment=0,
        impact_safety="Severe",
        impact_financial="Moderate",
        impact_operational="Severe",
        impact_privacy="Negligible",
        calculated_feasibility="High",
        calculated_impact="Severe",
        risk_level=5
    )

    jira_service = JiraSyncService()
    jira_res = jira_service.create_jira_issue(test_threat)
    assert "issue_key" in jira_res
    assert jira_res["synced_threat_id"] == "THR-ALM-101"

    jama_service = JamaSyncService()
    jama_res = jama_service.create_jama_item(test_threat)
    assert "item_id" in jama_res
    assert jama_res["synced_threat_id"] == "THR-ALM-101"


def test_alm_export_api_endpoints():
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "engineer", "password": "Eng@123"}
    ).json()
    token = login_res["access_token"]

    payload = {
        "threat_id": "THR-API-99",
        "target_asset": "ADAS ECU",
        "trust_boundary_id": "TB-01",
        "stride_category": "Spoofing",
        "mitre_attack_id": "T1110",
        "threat_description": "Spoofing ADAS camera Ethernet stream",
        "attack_path": ["Camera", "ADAS Controller"],
        "cybersecurity_requirement": "CSR-ADAS-01: Authenticate SOME/IP streams",
        "thales_mitigation_control": "Thales PKI",
        "citations": ["UNECE R155"],
        "elapsed_time": 1,
        "expertise": 3,
        "knowledge": 3,
        "window": 1,
        "equipment": 0,
        "impact_safety": "Severe",
        "impact_financial": "Major",
        "impact_operational": "Severe",
        "impact_privacy": "Negligible",
        "calculated_feasibility": "High",
        "calculated_impact": "Severe",
        "risk_level": 5
    }

    res_jira = client.post(
        "/api/v1/alm/jira/export",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_jira.status_code == 200
    assert res_jira.json()["status"] == "Completed"

    res_jama = client.post(
        "/api/v1/alm/jama/export",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_jama.status_code == 200
    assert res_jama.json()["status"] == "Completed"
