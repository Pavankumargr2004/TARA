"""
Unit tests for Few-Shot Prompt Templates and Prompt Formatting.
"""
from app.core.prompts import STRIDE_EXTRACTION_PROMPT, MITRE_MAPPING_PROMPT


def test_stride_extraction_prompt_formatting():
    context_text = "ECU-01 (Telematics) connects to ECU-02 (Gateway) via Ethernet 100Base-T1."
    formatted = STRIDE_EXTRACTION_PROMPT.format(
        context=context_text,
        asset="Gateway",
        boundary="TB-01"
    )
    assert context_text in formatted
    assert "Gateway" in formatted
    assert "TB-01" in formatted
    assert "ISO/SAE 21434" in formatted
    assert "STRIDE" in formatted


def test_mitre_mapping_prompt_formatting():
    formatted = MITRE_MAPPING_PROMPT.format(
        threat_description="Unauthorized firmware override via CAN bus",
        asset="Inverter ECU",
        stride="Tampering"
    )
    assert "Unauthorized firmware override" in formatted
    assert "Inverter ECU" in formatted
    assert "Tampering" in formatted
    assert "MITRE ATT&CK" in formatted
