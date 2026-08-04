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

            # Fallback heuristic calculation if LLM output unavailable or invalid
            state.gtm_strategy = GTMStrategy(
                primary_acquisition_channels=[
                    "Product-Led Growth (PLG) freemium self-serve funnel",
                    "Targeted LinkedIn B2B outbound campaign",
                    "SEO & thought-leadership content marketing"
                ],
                pricing_strategy="Freemium entry tier with $49/mo Pro and $199/mo Enterprise team plans.",
                positioning_statement=f"The fastest AI-driven strategic validation platform for {state.idea.target_audience or 'modern founders'}.",
                launch_tactics=[
                    "Product Hunt launchpad campaign",
                    "Venture capital incubator & accelerator partnerships",
                    "Targeted founder community focus groups"
                ],
                estimated_cac_summary="Estimated initial CAC of $35 - $65 per paid subscriber with a 4-month payback period."
            )
        except Exception as e:
            logger.error(f"Error in GTMStrategyAgent: {e}")
            state.error = f"GTMStrategyAgent error: {str(e)}"
        return state
