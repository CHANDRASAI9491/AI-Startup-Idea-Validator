import streamlit as st
from typing import Dict, List, Any


class ValidationProgressMonitor:
    """Real-time Progress Monitor for DeepAgents and LangGraph execution steps."""

    def __init__(self):
        self.step_names = {
            "planner": "Strategic Research Planning & Hypothesis Framing",
            "web_search": "Tavily Live Market & Competitive Intelligence",
            "market_analysis": "Market Sizing & Growth Opportunity (TAM/SAM/SOM)",
            "competitor_analysis": "Competitive Landscape & Moat Mapping",
            "swot_risk": "SWOT Matrix & Risk Severity Quantification",
            "mvp_recommendation": "MVP Feature Scoping & Tech Architecture",
            "gtm_strategy": "Go-To-Market & Acquisition Channel Strategy",
            "report": "Executive Synthesis & Viability Scoring",
        }
        self.status_box = None
        self._completed_steps = set()
        try:
            self.status_box = st.status("Validating startup concept with AI research pipeline...", expanded=True)
            self.status_box.write("Initializing multi-agent validation pipeline...")
        except Exception:
            self.status_box = None

    def update(self, step_id: str, status: str) -> None:
        """Progress update callback matching actual backend stages."""
        if not self.status_box:
            return
        label = self.step_names.get(step_id, step_id.replace("_", " ").title())
        try:
            if status == "in_progress":
                self.status_box.update(label=f"Analyzing: {label}...", state="running")
                self.status_box.write(f"&bull; **{label}**: Researching...")
            elif status == "completed":
                self._completed_steps.add(step_id)
                if len(self._completed_steps) >= len(self.step_names):
                    self.status_box.update(
                        label="Validation complete! Strategic due diligence report ready.",
                        state="complete",
                        expanded=False,
                    )
                else:
                    self.status_box.write(f"&#10003; **{label}**: Complete")
        except Exception:
            pass
