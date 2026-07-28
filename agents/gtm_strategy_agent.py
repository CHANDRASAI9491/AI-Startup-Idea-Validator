import logging
from agents.base_agent import BaseAgent
from state.schema import StartupIdea, GTMStrategy

logger = logging.getLogger(__name__)


class GTMStrategyAgent(BaseAgent):

    def run(self, idea: StartupIdea) -> GTMStrategy:
        prompt = f"""
Formulate a Go-To-Market (GTM) strategy for this startup concept.

Startup Idea: {idea.idea_text}
Target Industry: {idea.target_industry}
Target Audience: {idea.target_audience}

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
                return GTMStrategy.model_validate(json_data)
            except Exception as e:
                logger.warning(f"GTMStrategy parsing error: {e}")

        # Fallback GTM strategy
        return GTMStrategy(
            primary_acquisition_channels=[
                "Organic Content & SEO Marketing",
                f"Community outreach on Reddit, IndieHackers & Twitter/X in {idea.target_industry}",
                "Product-led onboarding with shareable report links"
            ],
            pricing_strategy="Freemium model: 1 free validation report, $29/mo for unlimited reports and export features.",
            positioning_statement=f"For {idea.target_audience} seeking rapid feedback on early-stage concepts, our platform provides instant, data-backed validation reports in seconds.",
            launch_tactics=[
                "Launch Show HN post on Hacker News",
                "Product Hunt submission with video demo",
                "Direct outreach to 50 target customer leads for feedback"
            ],
            estimated_cac_summary="Estimated initial CAC ($15 - $35) focusing on inbound organic community build."
        )
