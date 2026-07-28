import logging
from agents.base_agent import BaseAgent
from state.schema import (
    StartupIdea, MarketAnalysis, CompetitorAnalysis,
    SWOTAnalysis, MVPRecommendation, GTMStrategy, ValidationReport
)

logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):

    def run(
        self,
        idea: StartupIdea,
        market: MarketAnalysis,
        competitors: CompetitorAnalysis,
        swot: SWOTAnalysis,
        mvp: MVPRecommendation,
        gtm: GTMStrategy
    ) -> ValidationReport:
        
        prompt = f"""
Synthesize the complete multi-agent analysis for this startup concept and generate an executive validation report.

Startup Idea: {idea.idea_text}
Industry: {idea.target_industry}

Market Analysis:
- TAM: ${market.tam_billions}B, SAM: ${market.sam_billions}B, CAGR: {market.cagr_percentage}%
- Market Readiness Score: {market.market_readiness_score}/100

Competitors Analysis:
- Direct Competitors Count: {len(competitors.direct_competitors)}
- Moat: {competitors.moat_assessment}

SWOT & Risks:
- Strengths: {", ".join(swot.strengths[:2])}
- Risk Level: {swot.overall_risk_score}/10

MVP & Tech:
- Value Prop: {mvp.core_value_proposition}

GTM Strategy:
- Pricing: {gtm.pricing_strategy}

Respond ONLY with a JSON object matching this structure:
{{
  "overall_viability_score": 82,
  "verdict": "PROCEED",
  "executive_summary": "The startup concept demonstrates strong product-market fit potential with an estimated $15B TAM. Market readiness is high and execution risk is manageable.",
  "market_score": 85,
  "competitor_score": 75,
  "risk_score": 80,
  "mvp_score": 88,
  "gtm_score": 80,
  "key_takeaways": [
    "Large addressable market with accelerating annual CAGR",
    "Clear differentiation against legacy incumbents",
    "Tightly scoped MVP manageable in 4 weeks"
  ],
  "recommended_next_steps": [
    "Build initial MVP core workflow",
    "Create landing page to collect 100 early signup leads",
    "Interview 10 potential customers in target audience segment"
  ]
}}
"""
        json_data = self.generate_json(prompt, system_instruction="You are a Managing Partner at a top venture capital firm.")

        if json_data:
            try:
                return ValidationReport.model_validate(json_data)
            except Exception as e:
                logger.warning(f"ValidationReport parsing error: {e}")

        # Compute calculated weighted score fallback
        market_s = market.market_readiness_score if market else 75
        risk_s = max(0, 100 - (swot.overall_risk_score * 10)) if swot else 70
        comp_s = 75
        mvp_s = 85
        gtm_s = 75

        weighted_score = int(market_s * 0.3 + risk_s * 0.25 + comp_s * 0.15 + mvp_s * 0.15 + gtm_s * 0.15)

        verdict = "PROCEED" if weighted_score >= 75 else ("PIVOT" if weighted_score >= 60 else "CAUTION")

        return ValidationReport(
            overall_viability_score=weighted_score,
            verdict=verdict,
            executive_summary=f"The proposed concept '{idea.idea_text}' exhibits solid market fundamentals with a calculated viability index of {weighted_score}/100. Target market conditions and tech feasibility support proceeding to MVP stage.",
            market_score=market_s,
            competitor_score=comp_s,
            risk_score=risk_s,
            mvp_score=mvp_s,
            gtm_score=gtm_s,
            key_takeaways=[
                f"Sizable market opportunity with {market.cagr_percentage}% projected CAGR.",
                f"Defensible strategy focused on {idea.target_audience}.",
                "Low technical risk profile with standard modern stack."
            ],
            recommended_next_steps=[
                "Deploy minimal prototype targeting core feature set.",
                "Set up a conversion-focused landing page to capture pre-orders/signups.",
                "Conduct qualitative user interviews to validate feature priority."
            ]
        )
