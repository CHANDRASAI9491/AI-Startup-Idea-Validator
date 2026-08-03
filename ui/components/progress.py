import streamlit as st


class ValidationProgressMonitor:
    """Renders enterprise agent execution progress, active step indicator, and execution logs."""

    def __init__(self):
        self.progress_bar = st.progress(0)
        self.status_container = st.empty()

    def update(self, step_id: str, status: str):
        step_map = {
            "planner": (10, "DeepAgents Strategic Research Planning"),
            "web_search": (25, "Tavily Web Research and Market Snippet Gathering"),
            "market_analysis": (40, "Evaluating TAM/SAM/SOM and Market Growth"),
            "competitor_analysis": (55, "Analyzing Competitor Matrix and Positioning"),
            "swot_risk": (70, "Assessing SWOT and Calculating Risk Scores"),
            "mvp_recommendation": (85, "Scoping MVP Feature Set and Tech Stack"),
            "gtm_strategy": (92, "Formulating Go-To-Market Strategy"),
            "report": (100, "Synthesizing Executive Validation Report")
        }

        if step_id in step_map:
            pct, desc = step_map[step_id]
            self.progress_bar.progress(pct)
            self.status_container.markdown(
                f"""
                <div class="animated-progress-status" style="background-color: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; padding: 12px 16px; border-radius: 8px; font-size: 0.95rem; margin: 12px 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">
                    <strong>Active Running Agent:</strong> {desc} [<span style="text-transform: uppercase;">{status}</span>]
                </div>
                """,
                unsafe_allow_html=True
            )
