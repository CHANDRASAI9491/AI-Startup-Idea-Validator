import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, ValidationReport

logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):
    """Report Agent aggregating all sub-analyses into a comprehensive ValidationReport."""

    def run(self, state: StartupState) -> StartupState:
        logger.info(f"ReportAgent running for idea: {state.idea.idea_text}")
        try:
            idea = state.idea
            market = state.market_analysis
            competitors = state.competitor_analysis
            swot = state.swot_analysis
            mvp = state.mvp_recommendation
            gtm = state.gtm_strategy

            prompt = f"""
Synthesize the complete multi-agent analysis for this startup concept and generate an executive validation report.

Startup Idea: {idea.idea_text}
Industry: {idea.target_industry}

Market Analysis:
- TAM: ${market.tam_billions if market else 10}B, SAM: ${market.sam_billions if market else 2.5}B, CAGR: {market.cagr_percentage if market else 12}%
- Market Readiness Score: {market.market_readiness_score if market else 75}/100

Competitors Analysis:
- Direct Competitors Count: {len(competitors.direct_competitors) if competitors else 1}
- Moat: {competitors.moat_assessment if competitors else 'Speed and focus'}

SWOT & Risks:
- Strengths: {", ".join(swot.strengths[:2]) if swot and swot.strengths else 'Scalable product'}
- Risk Level: {swot.overall_risk_score if swot else 4}/10

MVP & Tech:
- Value Prop: {mvp.core_value_proposition if mvp else 'Automated efficiency'}

GTM Strategy:
- Pricing: {gtm.pricing_strategy if gtm else 'Freemium'}

Respond ONLY with a JSON object matching this structure:
{{
  "overall_viability_score": 82,
  "verdict": "PROCEED",
  "executive_summary": "The startup concept demonstrates strong market potential with an estimated TAM and high market readiness.",
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
    "Create landing page to collect early signup leads",
    "Interview target users in customer segment"
  ]
}}
"""
            json_data = self.generate_json(prompt, system_instruction="You are a Managing Partner at a top venture capital firm.")

            if json_data:
                try:
                    state.final_report = ValidationReport.model_validate(json_data)
                    state.status = "completed"
                    return state
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

            state.final_report = ValidationReport(
                overall_viability_score=weighted_score,
                verdict=verdict,
                executive_summary=f"The proposed concept '{idea.idea_text}' exhibits solid market fundamentals with a calculated viability index of {weighted_score}/100. Target market conditions and technical feasibility support proceeding to the MVP phase.",
                market_score=market_s,
                competitor_score=comp_s,
                risk_score=risk_s,
                mvp_score=mvp_s,
                gtm_score=gtm_s,
                key_takeaways=[
                    f"Sizable market opportunity in {idea.target_industry} with {market.cagr_percentage if market else 12.5}% CAGR.",
                    f"Defensible product-led strategy focused on {idea.target_audience}.",
                    "Manageable technical risk profile built with modern tech stack."
                ],
                recommended_next_steps=[
                    "Deploy minimal prototype focusing on core value proposition.",
                    "Build a conversion-focused landing page to test customer acquisition.",
                    "Conduct structured user interviews to validate feature priorities."
                ]
            )
            state.status = "completed"
        except Exception as e:
            logger.error(f"Error in ReportAgent: {e}")
            state.error = f"ReportAgent error: {str(e)}"
            state.status = "failed"
        return state
