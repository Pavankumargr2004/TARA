"""
Few-shot prompt templates for STRIDE & MITRE threat extraction.
"""

STRIDE_EXTRACTION_PROMPT = """You are an automotive cybersecurity analyst performing a TARA analysis
aligned with ISO/SAE 21434.

Given the following vehicle architecture context:
{context}

Identify all threat scenarios for the asset "{asset}" at trust boundary "{boundary}".

For each threat, provide:
1. STRIDE category (Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege)
2. MITRE ATT&CK for ICS/Auto technique ID
3. Detailed attack description
4. Multi-hop attack path from entry point to target
5. Cybersecurity requirement to mitigate
6. Thales defense control recommendation

Format as JSON array.

Example:
[
  {{
    "stride_category": "Tampering",
    "mitre_attack_id": "T1542",
    "threat_description": "Firmware manipulation via OTA update channel...",
    "attack_path": ["Public Cloud", "Cellular Modem", "Telematics ECU", "Gateway"],
    "cybersecurity_requirement": "CSR-OTA-01: Authenticate OTA payloads with eHSM keys",
    "thales_mitigation_control": "Thales eHSM Secure Boot & SUMS"
  }}
]
"""

MITRE_MAPPING_PROMPT = """Map the following automotive threat scenario to the most relevant
MITRE ATT&CK for ICS technique:

Threat: {threat_description}
Target Asset: {asset}
STRIDE Category: {stride}

Return the technique ID (e.g., T1542) and a brief justification.
"""
