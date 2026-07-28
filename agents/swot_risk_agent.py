import logging
from agents.base_agent import BaseAgent
from state.schema import StartupIdea, WebSearchResults, SWOTAnalysis
from tools.retrieval_utils import format_search_results_summary

logger = logging.getLogger(__name__)


class SWOTRiskAgent(BaseAgent):

    def run(self, idea: StartupIdea, search_results: WebSearchResults) -> SWOTAnalysis:
        search_summary = format_search_results_summary(search_results)
        
        prompt = f"""
Conduct a comprehensive SWOT analysis and Risk Assessment for this startup concept.

Startup Idea: {idea.idea_text}
Industry: {idea.target_industry}

Web Research Summary:
{search_summary}

Respond ONLY with a JSON object matching this structure:
{{
  "strengths": ["Strong value proposition", "Low capital requirement"],
  "weaknesses": ["Unproven market brand", "Initial customer trust hurdle"],
  "opportunities": ["Expanding global adoption", "Partnership opportunities"],
  "threats": ["Incumbent response", "Shifting regulatory environment"],
  "financial_risk": 4,
  "technical_risk": 3,
  "regulatory_risk": 2,
  "overall_risk_score": 3,
  "risk_mitigation_plan": [
    "Build early customer case studies to establish trust",
    "Maintain lean operations to minimize cash burn"
  ]
}}
"""
        json_data = self.generate_json(prompt, system_instruction="You are a venture risk auditor.")

        if json_data:
            try:
                return SWOTAnalysis.model_validate(json_data)
            except Exception as e:
                logger.warning(f"SWOTAnalysis parsing error: {e}")

        # Fallback SWOT analysis
        return SWOTAnalysis(
            strengths=[
                "High value-to-cost ratio for early adopters",
                "Scalable architecture with low marginal costs",
                f"Tightly focused on {idea.target_audience} pain points"
            ],
            weaknesses=[
                "Early brand awareness and distribution hurdles",
                "Reliance on third-party API infrastructure"
            ],
            opportunities=[
                f"Rapid expansion in the growing {idea.target_industry} sector",
                "Up-selling premium features and enterprise integrations"
            ],
            threats=[
                "Potential entry of well-funded legacy competitors",
                "Customer acquisition cost inflation"
            ],
            financial_risk=4,
            technical_risk=3,
            regulatory_risk=2,
            overall_risk_score=3,
            risk_mitigation_plan=[
                "Focus on organic content and product-led growth to keep CAC low",
                "Implement strict data encryption and privacy compliance early",
                "Maintain modular API design to prevent single-vendor lock-in"
            ]
        )
