import logging
from agents.base_agent import BaseAgent
from state.schema import StartupIdea, WebSearchResults, CompetitorAnalysis, CompetitorItem
from tools.retrieval_utils import format_search_results_summary

logger = logging.getLogger(__name__)


class CompetitorAgent(BaseAgent):

    def run(self, idea: StartupIdea, search_results: WebSearchResults) -> CompetitorAnalysis:
        search_summary = format_search_results_summary(search_results)
        
        prompt = f"""
Identify key competitors and market positioning for this startup idea based on research snippets.

Startup Idea: {idea.idea_text}
Industry: {idea.target_industry}

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
                return CompetitorAnalysis.model_validate(json_data)
            except Exception as e:
                logger.warning(f"CompetitorAnalysis parsing error: {e}")

        # Fallback competitor analysis
        return CompetitorAnalysis(
            direct_competitors=[
                CompetitorItem(
                    name="Established Market Player",
                    url="https://example.com/competitor1",
                    description=f"Existing provider of traditional {idea.target_industry} software.",
                    key_features=["Core management", "Standard reporting"],
                    pricing_model="Enterprise SaaS ($99 - $499/mo)",
                    strengths=["Existing customer base", "Brand recognition"],
                    weaknesses=["High price tag", "Slower innovation cycles"]
                )
            ],
            indirect_competitors=[
                CompetitorItem(
                    name="Manual / Spreadsheet Workarounds",
                    url="",
                    description="In-house manual scripts and spreadsheets.",
                    key_features=["Custom adaptability"],
                    pricing_model="Internal effort cost",
                    strengths=["Low explicit software cost"],
                    weaknesses=["Error-prone, lacks automated insights"]
                )
            ],
            feature_comparison_matrix={
                "Automation Level": {"Proposed Startup": "High (AI-Driven)", "Incumbents": "Low / Manual"},
                "Ease of Setup": {"Proposed Startup": "Instant (<10 mins)", "Incumbents": "Requires Onboarding"}
            },
            market_positioning_summary=f"Positioned as an agile, AI-first solution tailored specifically for modern {idea.target_audience}.",
            moat_assessment="Strong data flywheel, intuitive UI experience, and automated insight speed."
        )
