import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, MVPRecommendation, MVPFeature
from pipeline.context_passer import ContextPasser
from services.logger import get_logger

logger = get_logger(__name__)


class MVPRecommendationAgent(BaseAgent):
    """MVP Recommendation Agent scoping UVP, tech stack, feature breakdown, and 4-week roadmap."""

    def execute(self, state: StartupState) -> StartupState:
        logger.info(f"MVPRecommendationAgent scoping MVP for idea: '{state.idea.idea_text}'")
        try:
            context_summary = ContextPasser.extract_summary(state)

            prompt = self.load_prompt(
                "mvp_agent",
                idea_text=state.idea.idea_text,
                budget=state.idea.budget or "Bootstrap ($5k - $50k)",
                timeline=state.idea.timeline or "3 Months",
                context_summary=context_summary
            )

            json_data = self.generate_json(
                prompt,
                system_instruction="You are a Principal Product Architect and Fractional CTO."
            )

            if json_data:
                try:
                    state.mvp_recommendation = MVPRecommendation.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"MVPRecommendation parsing error: {e}")

            # If LLM output is unavailable or invalid, do not substitute fabricated MVP architecture
            state.mvp_recommendation = None
        except Exception as e:
            logger.error(f"Error in MVPRecommendationAgent: {e}")
            state.error = f"MVPRecommendationAgent error: {str(e)}"
            state.mvp_recommendation = None
        return state
