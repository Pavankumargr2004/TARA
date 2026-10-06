"""
Automotive Architecture Parsers: AUTOSAR ARXML and CAN DBC.
Extracts ECU topologies, CAN signals, trust boundaries, and ASIL ratings.
"""
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any


class AutosarArxmlParser:
    """Parses AUTOSAR System Description (.arxml) files."""
    
    @staticmethod
    def parse_arxml_string(xml_content: str) -> Dict[str, Any]:
        """Parse raw ARXML string and extract architectural components."""
        try:
            # Strip namespace for simplified tag matching
            xml_clean = re.sub(r'\sxmlns="[^"]+"', '', xml_content, count=1)
            root = ET.fromstring(xml_clean)
        except Exception as e:
            raise ValueError(f"Invalid ARXML format: {e}")
            
        ecus = []
        for ecu in root.findall(".//ECU-INSTANCE"):
            name = ecu.findtext("SHORT-NAME", "Unknown_ECU")
            domain = ecu.findtext("DOMAIN", "General")
            bus = ecu.findtext("BUS-REF", "CAN")
            asil = ecu.findtext("SECURITY-LEVEL", "QM")
            ecus.append({
                "name": name,
                "domain": domain,
                "bus": bus,
                "asil": asil
            })
            
        trust_boundaries = []
        for tb in root.findall(".//BOUNDARY"):
            tb_id = tb.attrib.get("id", "TB-00")
            risk = tb.attrib.get("risk", "Medium")
            stride = tb.attrib.get("stride", "Spoofing")
            source = tb.findtext("SOURCE", "External")
            target = tb.findtext("TARGET", "Internal")
            interface = tb.findtext("INTERFACE", "Ethernet")
            csr = tb.findtext("CSR", "Enforce message authentication.")
            
            trust_boundaries.append({
                "id": tb_id,
                "risk": risk,
                "stride": stride,
                "source": source,
                "target": target,
                "interface": interface,
                "csr": csr
            })
            
        system_name = root.findtext(".//SYSTEM/SHORT-NAME", "AUTOSAR_System")
        
        return {
            "system_name": system_name,
            "format": "AUTOSAR_ARXML",
            "ecus": ecus,
            "trust_boundaries": trust_boundaries,
            "raw_text_summary": f"AUTOSAR System '{system_name}' with {len(ecus)} ECUs and {len(trust_boundaries)} Trust Boundaries."
        }


class CanDbcParser:
    """Parses CAN Network Database (.dbc) files."""

    @staticmethod
    def parse_dbc_string(dbc_content: str) -> Dict[str, Any]:
        """Parse raw DBC string and extract CAN messages, signals, ECUs, and trust boundaries."""
        ecus = set()
        messages = []
        trust_boundaries = []
        
        lines = dbc_content.splitlines()
        current_msg = None
        
        for line in lines:
            line = line.strip()
            
            # Extract ECU Node List
            if line.startswith("BU_:"):
                nodes = line.replace("BU_:", "").strip().split()
                ecus.update(nodes)
                
            # Extract CAN Messages: BO_ <CAN_ID> <Message_Name>: <DLC> <Transmitter_ECU>
            elif line.startswith("BO_"):
                parts = line.split()
                if len(parts) >= 5:
                    can_id = parts[1]
                    msg_name = parts[2].rstrip(":")
                    dlc = parts[3]
                    tx_ecu = parts[4]
                    ecus.add(tx_ecu)
                    current_msg = {
                        "can_id": can_id,
                        "name": msg_name,
                        "dlc": dlc,
                        "transmitter": tx_ecu,
                        "signals": []
                    }
                    messages.append(current_msg)
                    
            # Extract CAN Signals: SG_ <Signal_Name> : <StartBit>|<Length>@... <Scale,Offset> [<Min>|<Max>] "<Unit>" <Receiver_ECU>
            elif line.startswith("SG_") and current_msg is not None:
                sg_match = re.match(r"SG_\s+(\w+)\s*:\s*(\d+)\|(\d+)@\d+[\+-]\s*\(([^\)]+)\)\s*\[([^\]]+)\]\s*\"([^\"]*)\"\s*(\w+)", line)
                if sg_match:
                    sig_name, start_bit, length, factor_offset, min_max, unit, rx_ecu = sg_match.groups()
                    ecus.add(rx_ecu)
                    current_msg["signals"].append({
                        "name": sig_name,
                        "start_bit": start_bit,
                        "length": length,
                        "unit": unit,
                        "receiver": rx_ecu
                    })
                    
            # Extract Trust Boundary Comments
            elif "# Trust Boundary" in line or "# Security Control" in line or "# Requirement" in line:
                trust_boundaries.append(line.lstrip("#").strip())

        ecu_list = [{"name": e, "domain": "Powertrain/CAN", "bus": "CAN FD", "asil": "ASIL-D" if "BMS" in e or "Inverter" in e else "QM"} for e in sorted(ecus)]

        return {
            "system_name": "CAN_Network_Database",
            "format": "CAN_DBC",
            "ecus": ecu_list,
            "messages": messages,
            "trust_boundaries_comments": trust_boundaries,
            "raw_text_summary": f"CAN DBC Network with {len(ecu_list)} ECUs, {len(messages)} CAN Messages, and {sum(len(m['signals']) for m in messages)} Signals."
        }
