import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, CompetitorAnalysis, CompetitorItem
from tools.retrieval_utils import format_search_results_summary
from services.logger import get_logger

logger = get_logger(__name__)


class CompetitorAgent(BaseAgent):
    """Competitor Analysis Agent evaluating direct/indirect incumbents, feature matrix, and moat defensibility."""

    def execute(self, state: StartupState) -> StartupState:
        logger.info(f"CompetitorAgent analyzing market landscape for idea: '{state.idea.idea_text}'")
        try:
            search_summary = format_search_results_summary(state.search_results)

            prompt = self.load_prompt(
                "competitor_agent",
                idea_text=state.idea.idea_text,
                target_industry=state.idea.target_industry or "Technology",
                search_summary=search_summary
            )

            json_data = self.generate_json(
                prompt,
                system_instruction="You are a Principal Competitive Intelligence Analyst."
            )

            if json_data:
                try:
                    state.competitor_analysis = CompetitorAnalysis.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"CompetitorAnalysis parsing error: {e}")

            # Honest unavailable representation if LLM output unavailable or invalid
            state.competitor_analysis = CompetitorAnalysis(
                direct_competitors=[],
                indirect_competitors=[],
                feature_comparison_matrix={},
                market_positioning_summary="No verified competitors identified from available research.",
                moat_assessment="Defensibility cannot be evaluated without verified competitor evidence."
            )
        except Exception as e:
            logger.error(f"Error in CompetitorAgent: {e}")
            state.error = f"CompetitorAgent error: {str(e)}"
        return state
