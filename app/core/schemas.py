from pydantic import BaseModel, Field
from typing import List, Optional

class TrustBoundary(BaseModel):
    boundary_id: str
    source_domain: str        # e.g., "External / Cloud"
    target_domain: str        # e.g., "Vehicle Gateway Subnet"
    interface_type: str       # e.g., "Cellular / OTA / BLE / OBD-II"
    exposure_level: str       # "High", "Medium", "Low"

class ThreatScenario(BaseModel):
    threat_id: str
    target_asset: str
    trust_boundary_id: Optional[str]
    stride_category: str      # Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation of Privilege
    mitre_attack_id: str      # e.g., "T1542" (Firmware Tampering), "T1059" (Command Scripting)
    threat_description: str
    attack_path: List[str]    # ["Cellular Network", "Telematics ECU", "Gateway", "Brake ECU"]
    cybersecurity_requirement: str
    thales_mitigation_control: str # e.g., "Thales eHSM Secure Boot & SUMS"
    citations: List[str]
    elapsed_time: int
    expertise: int
    knowledge: int
    window: int
    equipment: int
    impact_safety: str
    impact_financial: str
    impact_operational: str
    impact_privacy: str
    calculated_feasibility: Optional[str] = None
    calculated_impact: Optional[str] = None
    risk_level: Optional[int] = None
    review_status: str = "Pending Review"
    reviewer_notes: Optional[str] = ""
