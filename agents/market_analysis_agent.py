import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, MarketAnalysis, TargetPersona
from tools.retrieval_utils import format_search_results_summary
from services.logger import get_logger

logger = get_logger(__name__)


class MarketAnalysisAgent(BaseAgent):
    """Market Analysis Agent evaluating TAM/SAM/SOM market sizes, CAGR growth, drivers, and personas."""

    def execute(self, state: StartupState) -> StartupState:
        logger.info(f"MarketAnalysisAgent executing for idea: '{state.idea.idea_text}'")
        try:
            search_summary = format_search_results_summary(state.search_results)

            prompt = self.load_prompt(
                "market_analysis_agent",
                idea_text=state.idea.idea_text,
                target_industry=state.idea.target_industry or "Technology / SaaS",
                target_audience=state.idea.target_audience or "General Users / Businesses",
                search_summary=search_summary
            )

            json_data = self.generate_json(
                prompt,
                system_instruction="You are an expert market intelligence analyst."
            )

            if json_data:
                try:
                    state.market_analysis = MarketAnalysis.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"MarketAnalysis parsing error: {e}")

            # Honest unavailable representation if LLM output unavailable or invalid
            state.market_analysis = MarketAnalysis(
                tam_billions=None,
                sam_billions=None,
                som_billions=None,
                market_size_summary="Market size could not be established from available research.",
                cagr_percentage=None,
                key_growth_drivers=[],
                target_personas=[],
                market_readiness_score=None
            )
        except Exception as e:
            logger.error(f"Error in MarketAnalysisAgent: {e}")
            state.error = f"MarketAnalysisAgent error: {str(e)}"
        return state
