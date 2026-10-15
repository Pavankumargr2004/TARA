"""
Compliance export service — CSV and PDF generation for ISO/SAE 21434 audits.
"""
from typing import List
import pandas as pd
from app.core.schemas import ThreatScenario
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas


class ExportService:
    @staticmethod
    def to_csv(threats: List[ThreatScenario], output_path: str) -> str:
        data = [t.model_dump() for t in threats]
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        return output_path

    @staticmethod
    def to_pdf(threats: List[ThreatScenario], output_path: str, system_name: str = "Connected Vehicle System") -> str:
        c = pdf_canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        # Title Banner
        c.setFillColorRGB(0.05, 0.03, 0.15)
        c.rect(0, height - 90, width, 90, stroke=0, fill=1)

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 40, "ISO/SAE 21434 & UNECE R155 COMPLIANCE AUDIT REPORT")

        c.setFillColorRGB(0.77, 0.71, 0.99)
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 60, f"System Architecture: {system_name}  |  Classification: OEM Confidential")

        import datetime
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        c.setFont("Helvetica", 8)
        c.drawString(40, height - 76, f"Generated: {now_str}  |  Framework: ISO 21434:2021 & UN Regulation No. 155")

        # Executive Metrics Bar
        c.setFillColorRGB(0.96, 0.97, 0.99)
        c.rect(40, height - 125, width - 80, 25, stroke=1, fill=1)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("Helvetica-Bold", 8.5)
        tot = len(threats)
        apprv = sum(1 for t in threats if getattr(t, 'review_status', 'Pending Review') == 'Approved')
        crit = sum(1 for t in threats if getattr(t, 'risk_level', 1) >= 5)
        c.drawString(50, height - 117, f"TOTAL THREATS: {tot}     |     APPROVED: {apprv}     |     CRITICAL RISK (LVL 5): {crit}")

        c.setFont("Helvetica", 9)
        y = height - 150
        for idx, t in enumerate(threats):
            if y < 110:
                c.showPage()
                # Repeat compact header on subsequent pages
                c.setFillColorRGB(0.05, 0.03, 0.15)
                c.rect(0, height - 40, width, 40, stroke=0, fill=1)
                c.setFillColorRGB(1, 1, 1)
                c.setFont("Helvetica-Bold", 10)
                c.drawString(40, height - 25, f"ISO/SAE 21434 AUDIT REPORT — {system_name}")
                c.setFont("Helvetica", 9)
                y = height - 60

            # Threat card border
            c.setStrokeColorRGB(0.8, 0.82, 0.9)
            c.setFillColorRGB(0.98, 0.98, 1.0)
            c.rect(40, y - 55, width - 80, 58, stroke=1, fill=1)

            c.setFillColorRGB(0.1, 0.1, 0.2)
            c.setFont("Helvetica-Bold", 9.5)
            c.drawString(48, y - 12, f"[{t.threat_id}] {t.target_asset}")

            c.setFont("Helvetica", 8)
            c.drawString(380, y - 12, f"Status: {getattr(t, 'review_status', 'Pending Review')}")

            c.setFont("Helvetica", 8)
            c.setFillColorRGB(0.25, 0.25, 0.35)
            c.drawString(48, y - 25, f"STRIDE: {t.stride_category}  |  MITRE: {t.mitre_attack_id}  |  Feasibility: {t.calculated_feasibility}  |  Impact: {t.calculated_impact}  |  Risk Level: {t.risk_level}/5")

            c.drawString(48, y - 37, f"CSR: {str(t.cybersecurity_requirement)[:95]}...")
            c.drawString(48, y - 49, f"Mitigation: {str(t.thales_mitigation_control)[:95]}")

            y -= 70

        c.save()
        return output_path
