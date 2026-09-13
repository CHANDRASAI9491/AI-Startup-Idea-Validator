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

            # If LLM output is unavailable or invalid, do not fabricate SWOT/risk metrics
            state.swot_analysis = None
        except Exception as e:
            logger.error(f"Error in SWOTRiskAgent: {e}")
            state.error = f"SWOTRiskAgent error: {str(e)}"
            state.swot_analysis = None
        return state
