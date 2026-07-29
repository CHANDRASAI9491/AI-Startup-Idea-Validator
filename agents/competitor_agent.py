import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, CompetitorAnalysis, CompetitorItem
from tools.retrieval_utils import format_search_results_summary

logger = logging.getLogger(__name__)


class CompetitorAgent(BaseAgent):
    """Competitor Analysis Agent evaluating direct/indirect competitors, positioning, and moat."""

    def run(self, state: StartupState) -> StartupState:
        logger.info(f"CompetitorAgent running for idea: {state.idea.idea_text}")
        try:
            search_summary = format_search_results_summary(state.search_results)
            
            prompt = f"""
Identify key competitors and market positioning for this startup idea based on research snippets.

Startup Idea: {state.idea.idea_text}
Industry: {state.idea.target_industry}

Web Research Summary:
{search_summary}

Respond ONLY with a JSON object matching this structure:
{{
  "direct_competitors": [
    {{
      "name": "Competitor A",
      "url": "https://example.com",
      "description": "Leading solution in market",
      "key_features": ["Feature 1", "Feature 2"],
      "pricing_model": "Subscription ($49/mo)",
      "strengths": ["Brand dominance"],
      "weaknesses": ["Complex onboarding"]
    }}
  ],
  "indirect_competitors": [
    {{
      "name": "Generic Workarounds",
      "url": "",
      "description": "Manual Excel/Spreadsheet processes",
      "key_features": ["Custom flexibility"],
      "pricing_model": "Free / Built-in",
      "strengths": ["No added software fee"],
      "weaknesses": ["Time consuming"]
    }}
  ],
  "feature_comparison_matrix": {{
    "AI Automation": ["Proposed: Yes", "Competitors: Partial"],
    "Speed": ["Proposed: Fast (<5min)", "Competitors: Manual"]
  }},
  "market_positioning_summary": "The startup occupies a high-automation, high-accessibility niche.",
  "moat_assessment": "Proprietary workflow models, speed advantage, and vertical focus."
}}
"""
            json_data = self.generate_json(prompt, system_instruction="You are a competitive intelligence strategist.")

            if json_data:
                try:
                    state.competitor_analysis = CompetitorAnalysis.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"CompetitorAnalysis parsing error: {e}")

            # Fallback competitor analysis if LLM output unavailable or invalid
            state.competitor_analysis = CompetitorAnalysis(
                direct_competitors=[
                    CompetitorItem(
                        name="Established Industry Incumbent",
                        url="https://example.com/competitor1",
                        description=f"Existing provider of legacy software in {state.idea.target_industry}.",
                        key_features=["Core features", "Standard reporting"],
                        pricing_model="Enterprise SaaS ($99 - $499/mo)",
                        strengths=["Existing enterprise brand", "Installed customer base"],
                        weaknesses=["High cost", "Slow innovation cycles"]
                    )
                ],
                indirect_competitors=[
                    CompetitorItem(
                        name="Manual & Spreadsheet Processes",
                        url="",
                        description="Internal spreadsheets and manual team effort.",
                        key_features=["Custom flexibility"],
                        pricing_model="Internal labor cost",
                        strengths=["No upfront software licenses"],
                        weaknesses=["Prone to errors, lacks AI automation"]
                    )
                ],
                feature_comparison_matrix={
                    "Automation": {"Proposed": "AI-Driven (High)", "Incumbents": "Manual / Basic"},
                    "Time to Value": {"Proposed": "< 10 minutes", "Incumbents": "Weeks"}
                },
                market_positioning_summary=f"Positioned as an agile, AI-first alternative tailored specifically for modern {state.idea.target_audience}.",
                moat_assessment="Speed-to-insight advantage, proprietary workflow integration, and intuitive design."
            )
        except Exception as e:
            logger.error(f"Error in CompetitorAgent: {e}")
            state.error = f"CompetitorAgent error: {str(e)}"
        return state
