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
    def to_pdf(threats: List[ThreatScenario], output_path: str) -> str:
        c = pdf_canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "ISO/SAE 21434 TARA Compliance Report")

        c.setFont("Helvetica", 10)
        y = height - 80
        for t in threats:
            if y < 100:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50

            c.drawString(50, y, f"ID: {t.threat_id} | Asset: {t.target_asset}")
            y -= 15
            c.drawString(
                50, y,
                f"Risk Level: {t.risk_level} | "
                f"Feasibility: {t.calculated_feasibility} | "
                f"Impact: {t.calculated_impact}",
            )
            y -= 15
            c.drawString(50, y, f"Mitigation: {t.thales_mitigation_control}")
            y -= 25

        c.save()
        return output_path
