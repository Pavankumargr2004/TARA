"""
Unit tests for compliance export service (CSV and PDF generation).
"""
import os
import pytest
import pandas as pd
from app.services.export_service import ExportService
from app.core.schemas import ThreatScenario


@pytest.fixture
def sample_threats():
    return [
        ThreatScenario(
            threat_id="THR-EXP-01",
            target_asset="Gateway ECU",
            trust_boundary_id="TB-01",
            stride_category="Spoofing",
            mitre_attack_id="T1565",
            threat_description="CAN ID spoofing attack",
            attack_path=["OBD-II", "Gateway"],
            cybersecurity_requirement="CSR-GW-01: Message Authentication",
            thales_mitigation_control="Thales SecOC",
            citations=["ISO 21434"],
            elapsed_time=2,
            expertise=2,
            knowledge=1,
            window=2,
            equipment=1,
            impact_safety="Moderate",
            impact_financial="Low",
            impact_operational="Moderate",
            impact_privacy="Negligible",
            calculated_feasibility="Medium",
            calculated_impact="Moderate",
            risk_level=3
        ),
        ThreatScenario(
            threat_id="THR-EXP-02",
            target_asset="Braking ECU",
            trust_boundary_id="TB-02",
            stride_category="Tampering",
            mitre_attack_id="T1499",
            threat_description="Emergency stop command injection",
            attack_path=["Cellular", "Gateway", "Brake"],
            cybersecurity_requirement="CSR-BRK-01: Cryptographic MAC",
            thales_mitigation_control="Thales Luna HSM",
            citations=["ISO 26262 ASIL-D"],
            elapsed_time=3,
            expertise=3,
            knowledge=2,
            window=1,
            equipment=2,
            impact_safety="Severe",
            impact_financial="Major",
            impact_operational="Severe",
            impact_privacy="Negligible",
            calculated_feasibility="Low",
            calculated_impact="Severe",
            risk_level=4
        )
    ]


import tempfile

def test_export_to_csv(sample_threats):
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = os.path.join(tmp_dir, "compliance_report.csv")
        result = ExportService.to_csv(sample_threats, output_file)
        assert os.path.exists(result)

        df = pd.read_csv(result)
        assert len(df) == 2
        assert "threat_id" in df.columns
        assert "target_asset" in df.columns
        assert df.iloc[0]["threat_id"] == "THR-EXP-01"


def test_export_to_pdf(sample_threats):
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = os.path.join(tmp_dir, "compliance_report.pdf")
        result = ExportService.to_pdf(sample_threats, output_file)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 500


def test_export_empty_list_to_csv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = os.path.join(tmp_dir, "empty_report.csv")
        result = ExportService.to_csv([], output_file)
        assert os.path.exists(result)
        assert os.path.getsize(result) >= 0
