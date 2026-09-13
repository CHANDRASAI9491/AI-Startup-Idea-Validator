import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, GTMStrategy
from services.logger import get_logger

logger = get_logger(__name__)


class GTMStrategyAgent(BaseAgent):
    """Go-To-Market Strategy Agent formulating acquisition channels, pricing models, positioning, and tactics."""

    def execute(self, state: StartupState) -> StartupState:
        logger.info(f"GTMStrategyAgent formulating acquisition plan for idea: '{state.idea.idea_text}'")
        try:
            prompt = self.load_prompt(
                "gtm_agent",
                idea_text=state.idea.idea_text,
                business_model=state.idea.business_model or "B2B SaaS / Subscription",
                target_audience=state.idea.target_audience or "General Users / Businesses"
            )

            json_data = self.generate_json(
                prompt,
                system_instruction="You are a Senior SaaS Growth Marketer and GTM Strategist."
            )

            if json_data:
                try:
                    state.gtm_strategy = GTMStrategy.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"GTMStrategy parsing error: {e}")

            # If LLM output is unavailable or invalid, do not fabricate GTM assumptions
            state.gtm_strategy = None
        except Exception as e:
            logger.error(f"Error in GTMStrategyAgent: {e}")
            state.error = f"GTMStrategyAgent error: {str(e)}"
            state.gtm_strategy = None
        return state
