import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, ValidationReport
from services.scoring_engine import DeterministicScoringEngine
from pipeline.context_passer import ContextPasser
from services.logger import get_logger

logger = get_logger(__name__)


class ReportAgent(BaseAgent):
    """Report Agent compiling deterministic scores and synthesizing executive investor reports."""

    def execute(self, state: StartupState) -> StartupState:
        logger.info(f"ReportAgent synthesizing executive report for idea: '{state.idea.idea_text}'")
        try:
            # 1. Extract quantitative inputs from state for Deterministic Scoring Engine
            tam = state.market_analysis.tam_billions if state.market_analysis else 10.0
            sam = state.market_analysis.sam_billions if state.market_analysis else 2.5
            som = state.market_analysis.som_billions if state.market_analysis else 0.1
            cagr = state.market_analysis.cagr_percentage if state.market_analysis else 12.5
            
            comp_count = len(state.competitor_analysis.direct_competitors) if state.competitor_analysis else 3
            moat = state.competitor_analysis.moat_assessment if state.competitor_analysis else "Medium"
            
            fin_risk = state.swot_analysis.financial_risk if state.swot_analysis else 5
            tech_risk = state.swot_analysis.technical_risk if state.swot_analysis else 5
            reg_risk = state.swot_analysis.regulatory_risk if state.swot_analysis else 4

            # 2. CALCULATE SCORES DETERMINISTICALLY
            scoring_breakdown = DeterministicScoringEngine.calculate_scores(
                idea_text=state.idea.idea_text,
                target_industry=state.idea.target_industry or "Technology / SaaS",
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

            context_summary = ContextPasser.extract_summary(state)

            # 3. LLM Executive Narrative Synthesis
            prompt = self.load_prompt(
                "report_agent",
                idea_text=state.idea.idea_text,
                overall_viability_score=scoring_breakdown.total_viability_score,
                verdict=scoring_breakdown.verdict,
                reasoning_why="\n".join(f"- {r}" for r in scoring_breakdown.reasoning_why),
                context_summary=context_summary
            )

            json_data = self.generate_json(
                prompt,
                system_instruction="You are a Principal Venture Capital Partner and Lead Investment Analyst."
            )

            exec_summary = f"Executive Strategic Evaluation for '{state.idea.idea_text}' ({state.idea.target_industry}). Overall Viability Index is {scoring_breakdown.total_viability_score}/100 with a strategic verdict of {scoring_breakdown.verdict}."
            takeaways = [
                f"Deterministically scored overall viability index of {scoring_breakdown.total_viability_score}/100 based on an 8-dimension weighted matrix.",
                f"Target Market TAM of ${tam}B with projected CAGR of {cagr}%.",
                f"Strategic verdict classified as '{scoring_breakdown.verdict}'."
            ]
            next_steps = [
                "Build 4-week MVP focused on core automated workflow",
                "Conduct 15 customer discovery interviews",
                "Establish initial landing page for conversion validation"
            ]

            if json_data:
                exec_summary = json_data.get("executive_summary", exec_summary)
                takeaways = json_data.get("key_takeaways", takeaways)
                next_steps = json_data.get("recommended_next_steps", next_steps)

            state.final_report = ValidationReport(
                overall_viability_score=scoring_breakdown.total_viability_score,
                verdict=scoring_breakdown.verdict,
                executive_summary=exec_summary,
                scoring_breakdown=scoring_breakdown,
                market_score=int((scoring_breakdown.market_opportunity_score / 20.0) * 100),
                competitor_score=int((scoring_breakdown.competition_score / 15.0) * 100),
                risk_score=int((scoring_breakdown.execution_risk_score / 10.0) * 100),
                mvp_score=int((scoring_breakdown.technical_feasibility_score / 10.0) * 100),
                gtm_score=int((scoring_breakdown.scalability_score / 15.0) * 100),
                investor_readiness_score=scoring_breakdown.investor_readiness_score,
                funding_probability=scoring_breakdown.funding_probability,
                pmf_score=scoring_breakdown.pmf_score,
                confidence_score=scoring_breakdown.overall_confidence_score,
                key_takeaways=takeaways,
                recommended_next_steps=next_steps
            )
        except Exception as e:
            logger.error(f"Error in ReportAgent: {e}")
            state.error = f"ReportAgent error: {str(e)}"
        return state
