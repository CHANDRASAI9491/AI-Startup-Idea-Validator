import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, GTMStrategy

logger = logging.getLogger(__name__)


class GTMStrategyAgent(BaseAgent):
    """Go-To-Market Strategy Agent specifying channels, pricing, launch tactics, and positioning."""

    def run(self, state: StartupState) -> StartupState:
        logger.info(f"GTMStrategyAgent running for idea: {state.idea.idea_text}")
        try:
            prompt = f"""
Formulate a Go-To-Market (GTM) strategy for this startup concept.

Startup Idea: {state.idea.idea_text}
Target Industry: {state.idea.target_industry}
Target Audience: {state.idea.target_audience}

Respond ONLY with a JSON object matching this structure:
{{
  "primary_acquisition_channels": [
    "Product-Led Growth (Free Trial)",
    "Content Marketing & SEO",
    "Targeted LinkedIn Outbound"
  ],
  "pricing_strategy": "Freemium with $29/mo Starter & $99/mo Pro Tier",
  "positioning_statement": "For target users who need efficient solutions, our product delivers speed and automation unmatched by legacy tools.",
  "launch_tactics": [
    "Launch on Product Hunt & Hacker News (Show HN)",
    "Distribute early access invites to 100 beta testers",
    "Publish case study teardowns on industry blogs"
  ],
  "estimated_cac_summary": "Estimated initial CAC is low ($20-$50) by leveraging organic content and viral referral loops."
}}
"""
            json_data = self.generate_json(prompt, system_instruction="You are a startup Growth Marketer.")

            if json_data:
                try:
                    state.gtm_strategy = GTMStrategy.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"GTMStrategy parsing error: {e}")

            # Fallback GTM strategy if LLM output is unavailable or invalid
            state.gtm_strategy = GTMStrategy(
                primary_acquisition_channels=[
                    "Organic Search & Technical Content SEO",
                    f"Niche community engagement on Twitter/X, LinkedIn & Reddit within {state.idea.target_industry}",
                    "Product-led viral growth via shareable validation reports"
                ],
                pricing_strategy="Freemium model: 1 free validation, $29/mo for unlimited validation & export access.",
                positioning_statement=f"For {state.idea.target_audience} looking to validate startup ideas fast, our AI platform delivers comprehensive market research in minutes.",
                launch_tactics=[
                    "Launch Product Hunt campaign with interactive video demo",
                    "Post Show HN on Hacker News featuring live demo links",
                    "Direct outreach to 50 target customer leads for structured feedback"
                ],
                estimated_cac_summary="Estimated low initial CAC ($15 - $35) driven by organic community build and inbound content."
            )
        except Exception as e:
            logger.error(f"Error in GTMStrategyAgent: {e}")
            state.error = f"GTMStrategyAgent error: {str(e)}"
        return state
