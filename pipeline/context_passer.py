import logging
from typing import Dict, Any, Optional
from state.schema import StartupState, StartupIdea

logger = logging.getLogger(__name__)


class ContextPasser:
    """Helper utility for passing, validating, and formatting state context between LangGraph agent nodes."""

    @staticmethod
    def extract_summary(state: StartupState) -> str:
        """Extracts a structured text context summary of the state for agent consumption."""
        idea = state.idea
        summary_lines = [
            f"Startup Concept Description: {idea.idea_text}",
            f"Industry Sector: {idea.target_industry}",
            f"Target Customer Segment: {idea.target_audience}",
            f"Business Model: {idea.business_model}",
            f"Initial Budget: {idea.budget}",
            f"Target Launch Timeline: {idea.timeline}"
        ]

        if state.market_analysis:
            m = state.market_analysis
            summary_lines.append(f"Market Sizing: TAM=${m.tam_billions}B, SAM=${m.sam_billions}B, SOM=${m.som_billions}B, CAGR={m.cagr_percentage}%")

        if state.competitor_analysis:
            c = state.competitor_analysis
            summary_lines.append(f"Competitive Moat: {c.moat_assessment}")

        if state.swot_analysis:
            s = state.swot_analysis
            summary_lines.append(f"Risk Profile: Overall Risk={s.overall_risk_score}/10, Tech Risk={s.technical_risk}/10")

        return "\n".join(summary_lines)

    @staticmethod
    def validate_state_integrity(state: StartupState) -> bool:
        """Verifies that StartupState retains idea text and valid status."""
        if not state.idea or not state.idea.idea_text:
            logger.error("State integrity check failed: Missing idea_text description.")
            return False
        return True
