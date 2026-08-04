import streamlit as st
from typing import Dict, List, Any


class ValidationProgressMonitor:
    """Real-time Progress Monitor for DeepAgents and LangGraph execution steps."""

    def __init__(self):
        self.step_names = {
            "planner": "DeepAgents Strategic Research Planning",
            "web_search": "Tavily Web Research & Evidence Gathering",
            "market_analysis": "TAM/SAM/SOM & Market Sizing Evaluation",
            "competitor_analysis": "Competitive Matrix & Moat Mapping",
            "swot_risk": "SWOT Matrix & Risk Severity Calculation",
            "mvp_recommendation": "MVP Feature Scoping & Tech Architecture",
            "gtm_strategy": "Go-To-Market & Customer Acquisition Channels",
            "report": "Executive Validation Synthesis & Verdict"
        }

    def update(self, step_id: str, status: str) -> None:
        """Progress update callback."""
        pass
