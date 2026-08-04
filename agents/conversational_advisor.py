import logging
from typing import List, Dict, Optional
from agents.base_agent import BaseAgent
from state.schema import StartupState
from services.logger import get_logger

logger = get_logger(__name__)


class ConversationalAdvisor(BaseAgent):
    """Grounded Q&A Chatbot answering follow-up questions exclusively from generated report evidence."""

    def answer_question(self, user_question: str, state: StartupState, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        logger.info(f"ConversationalAdvisor answering user question: '{user_question}'")
        try:
            if not state or not state.final_report:
                return "No validation report data is available for this session. Please validate a startup concept first."

            report = state.final_report
            idea = state.idea
            scoring = report.scoring_breakdown

            report_context = f"""
Startup Concept: {idea.idea_text}
Industry Sector: {idea.target_industry} | Target Audience: {idea.target_audience} | Business Model: {idea.business_model}
Overall Viability Score: {report.overall_viability_score}/100
Strategic Verdict: {report.verdict}
Investor Readiness Score: {report.investor_readiness_score}/100
Funding Probability: {report.funding_probability}%
Product-Market Fit Score: {report.pmf_score}/100
Executive Summary: {report.executive_summary}
Key Takeaways: {', '.join(report.key_takeaways)}
Recommended Next Steps: {', '.join(report.recommended_next_steps)}
"""

            if scoring:
                report_context += f"\nExplainable Reasoning: {', '.join(scoring.reasoning_why)}"

            if state.market_analysis:
                m = state.market_analysis
                report_context += f"\nMarket Sizing: TAM=${m.tam_billions}B, SAM=${m.sam_billions}B, SOM=${m.som_billions}B, CAGR={m.cagr_percentage}%"

            if state.competitor_analysis:
                c = state.competitor_analysis
                report_context += f"\nCompetitive Moat: {c.moat_assessment} | Positioning: {c.market_positioning_summary}"

            if state.swot_analysis:
                s = state.swot_analysis
                report_context += f"\nRisk Profile: Overall Risk={s.overall_risk_score}/10 | Strengths: {', '.join(s.strengths)} | Weaknesses: {', '.join(s.weaknesses)}"

            if state.mvp_recommendation:
                mvp = state.mvp_recommendation
                report_context += f"\nMVP Tech Stack: Frontend ({mvp.tech_stack_frontend}), Backend ({mvp.tech_stack_backend}), AI ({mvp.tech_stack_ai})"

            history_str = ""
            if chat_history:
                history_lines = [f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in chat_history[-6:]]
                history_str = "\n".join(history_lines)

            prompt = self.load_prompt(
                "advisor_agent",
                report_context=report_context,
                chat_history_summary=history_str or "None",
                user_question=user_question
            )

            text_response = self.generate_text(
                prompt,
                system_instruction="You are an expert venture capital strategic advisor."
            )

            if text_response:
                return text_response

            # Fallback grounded answer
            return (
                f"Based on the generated validation report for **'{idea.idea_text}'**:\n\n"
                f"- **Viability Score:** {report.overall_viability_score}/100 ({report.verdict})\n"
                f"- **Investor Readiness:** {report.investor_readiness_score}/100 (Funding Probability: {report.funding_probability}%)\n"
                f"- **Executive Summary:** {report.executive_summary}\n\n"
                f"For your question: *'{user_question}'*, the report highlights that the primary next step is: {report.recommended_next_steps[0] if report.recommended_next_steps else 'Focus on MVP scoping'}."
            )
        except Exception as e:
            logger.error(f"Error in ConversationalAdvisor: {e}")
            return f"An error occurred while consulting the AI Advisor: {str(e)}"
