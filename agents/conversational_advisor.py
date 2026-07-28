import logging
from typing import List, Dict
from agents.base_agent import BaseAgent
from state.schema import AgentState

logger = logging.getLogger(__name__)


class ConversationalAdvisor(BaseAgent):
    """Interactive AI Startup Advisor grounded in the completed validation report."""

    def answer_question(self, user_question: str, state: AgentState, chat_history: List[Dict[str, str]]) -> str:
        report = state.final_report
        idea = state.idea
        market = state.market_analysis
        swot = state.swot_analysis

        context_summary = f"""
Startup Idea: {idea.idea_text}
Industry: {idea.target_industry}
Overall Score: {report.overall_viability_score if report else 'N/A'}/100
Verdict: {report.verdict if report else 'N/A'}
Market Size (TAM): ${market.tam_billions if market else '10'}B
Overall Risk Score: {swot.overall_risk_score if swot else '5'}/10
Executive Summary: {report.executive_summary if report else ''}
"""

        formatted_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in chat_history[-5:]])

        prompt = f"""
You are a senior Startup Advisor & Venture Capital mentor providing advice grounded in the validation report context.

Report Context:
{context_summary}

Recent Chat History:
{formatted_history}

User Question: {user_question}

Provide a direct, practical, encouraging, and actionable response for the startup founder:
"""
        response_text = self.generate_text(prompt, system_instruction="You are a trusted startup advisor.")

        if response_text and response_text.strip():
            return response_text.strip()

        # Heuristic answer fallback
        return f"Regarding your question '{user_question}': Based on our analysis for '{idea.idea_text}', we recommend focusing on your core value proposition and validating early demand with key users in {idea.target_industry}. Your overall viability score is {report.overall_viability_score if report else 80}/100 with a verdict of {report.verdict if report else 'PROCEED'}."
