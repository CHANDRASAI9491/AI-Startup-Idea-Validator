import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, SWOTAnalysis
from tools.retrieval_utils import format_search_results_summary

logger = logging.getLogger(__name__)


class SWOTRiskAgent(BaseAgent):
    """SWOT and Risk Agent conducting Strengths, Weaknesses, Opportunities, Threats, and Risk scores."""

    def run(self, state: StartupState) -> StartupState:
        logger.info(f"SWOTRiskAgent running for idea: {state.idea.idea_text}")
        try:
            search_summary = format_search_results_summary(state.search_results)
            
            prompt = f"""
Conduct a comprehensive SWOT analysis and Risk Assessment for this startup concept.

Startup Idea: {state.idea.idea_text}
Industry: {state.idea.target_industry}

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
                    state.swot_analysis = SWOTAnalysis.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"SWOTAnalysis parsing error: {e}")

            # Fallback SWOT analysis if LLM output is unavailable or invalid
            state.swot_analysis = SWOTAnalysis(
                strengths=[
                    "High value-to-cost ratio for early adopters",
                    "Scalable cloud architecture with low marginal server cost",
                    f"Tightly focused on {state.idea.target_audience} pain points"
                ],
                weaknesses=[
                    "Early brand awareness and customer acquisition trust hurdles",
                    "Dependency on continuous AI model availability"
                ],
                opportunities=[
                    f"Rapid expansion in the growing {state.idea.target_industry} sector",
                    "Up-selling enterprise tiers and custom team integrations"
                ],
                threats=[
                    "Potential copycat features from well-funded legacy competitors",
                    "Customer acquisition cost inflation across digital channels"
                ],
                financial_risk=4,
                technical_risk=3,
                regulatory_risk=2,
                overall_risk_score=3,
                risk_mitigation_plan=[
                    "Focus on product-led growth and referral incentives to keep CAC low",
                    "Implement strict data encryption and user privacy protocols",
                    "Design modular provider wrappers to ensure API vendor independence"
                ]
            )
        except Exception as e:
            logger.error(f"Error in SWOTRiskAgent: {e}")
            state.error = f"SWOTRiskAgent error: {str(e)}"
        return state
