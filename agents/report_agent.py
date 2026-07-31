import logging
from typing import Optional
from state.schema import StartupState, ValidationReport
from agents.base_agent import BaseAgent
from services.scoring_engine import DeterministicScoringEngine

logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):
    """Report Agent synthesizing deterministic scoring engine metrics and multi-agent outputs into an investor report."""

    def __init__(self, model_name: Optional[str] = None):
        super().__init__(model_name=model_name)

    def execute(self, state: StartupState) -> StartupState:
        logger.info("ReportAgent generating evidence-driven investor report...")

        idea = state.idea
        market = state.market_analysis
        comp = state.competitor_analysis
        swot = state.swot_analysis
        mvp = state.mvp_recommendation
        gtm = state.gtm_strategy

        tam = market.tam_billions if market else 10.0
        sam = market.sam_billions if market else 2.5
        som = market.som_billions if market else 0.1
        cagr = market.cagr_percentage if market else 12.5
        comp_count = len(comp.direct_competitors) if comp else 3
        moat = comp.moat_assessment if comp else "Medium"
        fin_risk = swot.financial_risk if swot else 5
        tech_risk = swot.technical_risk if swot else 5
        reg_risk = swot.regulatory_risk if swot else 4

        # Compute deterministic scores using the hybrid scoring engine
        scoring = DeterministicScoringEngine.calculate_scores(
            idea_text=idea.idea_text,
            target_industry=idea.target_industry or "Technology / SaaS",
            tam_billions=tam,
            sam_billions=sam,
            som_billions=som,
            cagr_percentage=cagr,
            direct_competitor_count=comp_count,
            moat_level=moat,
            financial_risk=fin_risk,
            technical_risk=tech_risk,
            regulatory_risk=reg_risk
        )

        prompt = f"""
Write an executive, evidence-based investor validation synthesis for this startup concept.

Startup Description: {idea.idea_text}
Industry Sector: {idea.target_industry}
Calculated Viability Score: {scoring.total_viability_score}/100
Calculated Verdict: {scoring.verdict}
Calculated Investor Readiness: {scoring.investor_readiness_score}/100
Calculated Funding Probability: {scoring.funding_probability}%

Key Scoring Drivers & WHY:
{chr(10).join(['- ' + r for r in scoring.reasoning_why])}

Respond ONLY with a JSON object matching this structure:
{{
  "executive_summary": "Comprehensive 3-paragraph executive summary detailing value prop, market opportunity, and key risks.",
  "key_takeaways": [
    "Takeaway 1 grounded in market sizing and TAM.",
    "Takeaway 2 grounded in competitive defensibility.",
    "Takeaway 3 grounded in technical/regulatory risk."
  ],
  "recommended_next_steps": [
    "Build interactive prototype for core feature set.",
    "Conduct customer discovery interviews with target persona.",
    "Establish initial IP or proprietary algorithm defensibility."
  ]
}}
"""
        json_data = self.llm_service.generate_json(prompt, system_instruction="You are a Senior Venture Capital Partner and Startup Analyst.")

        if json_data:
            report = ValidationReport(
                overall_viability_score=scoring.total_viability_score,
                verdict=scoring.verdict,
                executive_summary=json_data.get("executive_summary", f"Validation analysis yields a {scoring.total_viability_score}/100 score for concept '{idea.idea_text[:40]}...' in {idea.target_industry}."),
                scoring_breakdown=scoring,
                market_score=int((scoring.market_opportunity_score / 20.0) * 100),
                competitor_score=int((scoring.competition_score / 15.0) * 100),
                risk_score=int((scoring.execution_risk_score / 10.0) * 100),
                mvp_score=int((scoring.technical_feasibility_score / 10.0) * 100),
                gtm_score=int((scoring.scalability_score / 15.0) * 100),
                investor_readiness_score=scoring.investor_readiness_score,
                funding_probability=scoring.funding_probability,
                pmf_score=scoring.pmf_score,
                confidence_score=scoring.overall_confidence_score,
                key_takeaways=json_data.get("key_takeaways", scoring.reasoning_why),
                recommended_next_steps=json_data.get("recommended_next_steps", ["Conduct discovery interviews", "Build MVP prototype", "Establish early distribution"])
            )
            state.final_report = report
            return state

        # Fallback deterministic report
        state.final_report = ValidationReport(
            overall_viability_score=scoring.total_viability_score,
            verdict=scoring.verdict,
            executive_summary=f"Evidence-driven validation analysis for concept '{idea.idea_text}' in {idea.target_industry}. Market TAM is ${tam}B with a {cagr}% CAGR. Determined viability index is {scoring.total_viability_score}/100 with a strategic verdict of {scoring.verdict}.",
            scoring_breakdown=scoring,
            market_score=int((scoring.market_opportunity_score / 20.0) * 100),
            competitor_score=int((scoring.competition_score / 15.0) * 100),
            risk_score=int((scoring.execution_risk_score / 10.0) * 100),
            mvp_score=int((scoring.technical_feasibility_score / 10.0) * 100),
            gtm_score=int((scoring.scalability_score / 15.0) * 100),
            investor_readiness_score=scoring.investor_readiness_score,
            funding_probability=scoring.funding_probability,
            pmf_score=scoring.pmf_score,
            confidence_score=scoring.overall_confidence_score,
            key_takeaways=scoring.reasoning_why,
            recommended_next_steps=["Validate customer willingness to pay", "Scope 4-week MVP prototype", "Map customer acquisition channels"]
        )
        return state
