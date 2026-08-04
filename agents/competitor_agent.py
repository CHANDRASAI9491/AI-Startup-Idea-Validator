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

            # Fallback heuristic calculation if LLM output unavailable or invalid
            state.competitor_analysis = CompetitorAnalysis(
                direct_competitors=[
                    CompetitorItem(
                        name="Incumbent Core SaaS",
                        url="https://example.com/incumbent",
                        description=f"Established incumbent platform in {state.idea.target_industry}",
                        key_features=["Basic reporting", "Manual dashboard"],
                        pricing_model="Enterprise ($149/mo)",
                        strengths=["Brand awareness", "Large sales team"],
                        weaknesses=["High pricing", "Slow product iteration"]
                    ),
                    CompetitorItem(
                        name="Legacy Tooling Solution",
                        url="https://example.org/legacy",
                        description="Legacy desktop and spreadsheet workflow solution",
                        key_features=["Templates", "File exports"],
                        pricing_model="Perpetual license",
                        strengths=["Install base"],
                        weaknesses=["No AI automation", "No cloud sync"]
                    )
                ],
                indirect_competitors=[
                    CompetitorItem(
                        name="Custom Spreadsheets / Manual Workflows",
                        url="https://example.com/manual",
                        description="Internal manual team processes and custom spreadsheets",
                        pricing_model="Internal labor cost",
                        strengths=["Low upfront software cost"],
                        weaknesses=["High human error rate", "Non-scalable"]
                    )
                ],
                feature_comparison_matrix={
                    "AI Automation": {"Us": "Yes", "Incumbent Core": "Partial"},
                    "Cloud Synchronization": {"Us": "Yes", "Incumbent Core": "Yes"},
                    "Real-time Analytics": {"Us": "Yes", "Incumbent Core": "No"}
                },
                market_positioning_summary=f"Positions as an AI-first automated alternative in the {state.idea.target_industry} space.",
                moat_assessment="Defensible workflow automation, proprietary data loops, and rapid time-to-value."
            )
        except Exception as e:
            logger.error(f"Error in CompetitorAgent: {e}")
            state.error = f"CompetitorAgent error: {str(e)}"
        return state
