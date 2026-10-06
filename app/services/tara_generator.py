"""
TARA Generator — orchestrates RAG retrieval + deterministic risk scoring.
"""
import os
import uuid
from typing import List
from app.core.config import settings
from app.core.schemas import ThreatScenario
from app.core.risk_engine import (
    calculate_attack_potential,
    calculate_impact,
    impact_label_to_int,
    lookup_risk,
)
from app.services.rag_pipeline import RAGPipeline

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class TaraGenerator:
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag = rag_pipeline
        self.api_key = os.getenv("GEMINI_API_KEY", getattr(settings, "GEMINI_API_KEY", ""))

    def generate_threats_for_asset(
        self,
        asset_name: str,
        boundary: str,
        architecture_context: str,
    ) -> List[ThreatScenario]:
        query = (
            f"Find threat scenarios for asset {asset_name} "
            f"at boundary {boundary} within context {architecture_context}"
        )
        relevant_docs = self.rag.query(query, k=2)

        citations = [
            doc.metadata.get("source", "Unknown Source") for doc in relevant_docs
        ]

        desc = f"Potential spoofing attack on {asset_name} via {boundary}."
        csr = "Enforce mutual authentication and SecOC."

        # Real-time Gemini LLM response generation if key is present
        if self.api_key and HAS_GENAI:
            try:
                client = genai.Client(api_key=self.api_key)
                prompt = (
                    f"You are an ISO/SAE 21434 Automotive Cybersecurity expert. "
                    f"Analyze asset '{asset_name}' at boundary '{boundary}'. Context: {architecture_context}. "
                    f"Provide a 2-sentence threat scenario description and 1 cybersecurity requirement (CSR)."
                )
                res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                if res and res.text:
                    desc = res.text.strip()
            except Exception as e:
                print(f"Gemini LLM inference fallback: {e}")

        generated_threat = ThreatScenario(
            threat_id=f"THR-{uuid.uuid4().hex[:6].upper()}",
            target_asset=asset_name,
            trust_boundary_id=boundary,
            stride_category="Spoofing",
            mitre_attack_id="T1110",
            threat_description=desc,
            attack_path=["External", boundary, asset_name],
            cybersecurity_requirement=csr,
            thales_mitigation_control="Thales PKI & SecOC",
            citations=citations,
            elapsed_time=1,
            expertise=3,
            knowledge=3,
            window=1,
            equipment=0,
            impact_safety="Major",
            impact_financial="Moderate",
            impact_operational="Severe",
            impact_privacy="Negligible",
        )

        # Deterministic scoring
        feasibility = calculate_attack_potential(
            generated_threat.elapsed_time,
            generated_threat.expertise,
            generated_threat.knowledge,
            generated_threat.window,
            generated_threat.equipment,
        )
        impact_score = calculate_impact(
            impact_label_to_int(generated_threat.impact_safety),
            impact_label_to_int(generated_threat.impact_financial),
            impact_label_to_int(generated_threat.impact_operational),
            impact_label_to_int(generated_threat.impact_privacy),
        )
        risk = lookup_risk(impact_score, feasibility)

        generated_threat.calculated_feasibility = feasibility
        generated_threat.calculated_impact = (
            "Severe" if impact_score == 4
            else "Major" if impact_score == 3
            else "Moderate" if impact_score == 2
            else "Negligible"
        )
        generated_threat.risk_level = risk

        return [generated_threat]
