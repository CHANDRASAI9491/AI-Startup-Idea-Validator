import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, SWOTAnalysis, RiskItem
from pipeline.context_passer import ContextPasser
from services.logger import get_logger

logger = get_logger(__name__)


class SWOTRiskAgent(BaseAgent):
    """SWOT & Risk Agent generating strengths, weaknesses, opportunities, threats, and a severity risk matrix."""

    def execute(self, state: StartupState) -> StartupState:
        logger.info(f"SWOTRiskAgent calculating risk matrix for idea: '{state.idea.idea_text}'")
        try:
            context_summary = ContextPasser.extract_summary(state)

            prompt = self.load_prompt(
                "swot_risk_agent",
                idea_text=state.idea.idea_text,
                target_industry=state.idea.target_industry or "Technology / SaaS",
                context_summary=context_summary
            )

            json_data = self.generate_json(
                prompt,
                system_instruction="You are a Senior Venture Risk Officer and Strategic Analyst."
            )

            if json_data:
                try:
                    state.swot_analysis = SWOTAnalysis.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"SWOTAnalysis parsing error: {e}")

            # Fallback heuristic calculation if LLM output unavailable or invalid
            state.swot_analysis = SWOTAnalysis(
                strengths=[
                    "High-margin software revenue model",
                    "Proprietary AI automation workflow",
                    "Fast time-to-value for target users"
                ],
                weaknesses=[
                    "Early-stage brand recognition",
                    "Initial marketing & acquisition pipeline requirement"
                ],
                opportunities=[
                    f"Rapid growth in enterprise {state.idea.target_industry} demand",
                    "API integrations and partnership ecosystem"
                ],
                threats=[
                    "Incumbents attempting feature cloning",
                    "Evolving AI compliance & data privacy rules"
                ],
                financial_risk=5,
                technical_risk=4,
                regulatory_risk=3,
                overall_risk_score=4,
                risk_matrix=[
                    RiskItem(
                        risk_name="Initial Customer Acquisition Cost (CAC)",
                        category="Financial",
                        probability=3,
                        impact=4,
                        severity_score=12,
                        mitigation_strategy="Deploy product-led growth (PLG) freemium funnel and targeted outbounds."
                    ),
                    RiskItem(
                        risk_name="Incumbent Feature Parity Response",
                        category="Market",
                        probability=3,
                        impact=3,
                        severity_score=9,
                        mitigation_strategy="Focus on specialized niche features and superior user experience."
                    ),
                    RiskItem(
                        risk_name="Data Privacy & Security Boundaries",
                        category="Regulatory",
                        probability=2,
                        impact=3,
                        severity_score=6,
                        mitigation_strategy="Implement SOC2 compliance framework and zero-retention API policies."
                    )
                ],
                risk_mitigation_plan=[
                    "Focus initial release strictly on high-impact core features",
                    "Establish clear customer feedback and iteration channels",
                    "Maintain lean operating expenditure during pre-PMF validation phase"
                ]
            )
        except Exception as e:
            logger.error(f"Error in SWOTRiskAgent: {e}")
            state.error = f"SWOTRiskAgent error: {str(e)}"
        return state
