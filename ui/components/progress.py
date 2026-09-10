"""
Real-time Progress Monitor for DeepAgents and LangGraph execution steps.
Renders real pipeline stages and dynamic status updates.
"""

import html
import streamlit as st
from typing import Dict, List, Set, Optional


class ValidationProgressMonitor:
    """Real-time Progress Monitor for the multi-agent validation pipeline."""

    STAGES: List[Dict[str, str]] = [
        {"id": "planner", "name": "Hypothesis & Strategic Planning", "short": "Planning"},
        {"id": "web_search", "name": "Live Market & Intelligence Search (Tavily)", "short": "Research"},
        {"id": "market_analysis", "name": "Market Sizing & Opportunity (TAM/SAM/SOM)", "short": "Market Analysis"},
        {"id": "competitor_analysis", "name": "Competitor Landscape & Moat Mapping", "short": "Competition"},
        {"id": "swot_risk", "name": "SWOT Matrix & Risk Quantification", "short": "Risk / SWOT"},
        {"id": "mvp_recommendation", "name": "MVP Feature Architecture & Scoping", "short": "MVP Blueprint"},
        {"id": "gtm_strategy", "name": "Go-To-Market & Channel Strategy", "short": "GTM Strategy"},
        {"id": "report", "name": "Executive Synthesis & Deterministic Scoring", "short": "Scoring & Report"},
    ]

    def __init__(self):
        self._completed_steps: Set[str] = set()
        self._current_step: Optional[str] = None
        self.status_box = None
        self.pipeline_placeholder = None

        try:
            self.status_box = st.status(
                "Autonomous Validation Pipeline Running...",
                expanded=True
            )
            with self.status_box:
                self.pipeline_placeholder = st.empty()
                self._render_stepper()
        except Exception:
            self.status_box = None
            self.pipeline_placeholder = None

    def _render_stepper(self) -> None:
        """Renders the current visual state of the 8 real pipeline stages."""
        if not self.pipeline_placeholder:
            return

        items_html = []
        for idx, stage in enumerate(self.STAGES, start=1):
            s_id = stage["id"]
            name = html.escape(stage["name"])

            if s_id in self._completed_steps:
                icon = "&#10003;"
                status_class = "stage-completed"
                badge = '<span style="color: #059669; background: #ECFDF5; border: 1px solid #A7F3D0; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 12px;">Completed</span>'
                border_color = "#10B981"
                bg_color = "#F0FDF4"
                text_color = "#0F172A"
                icon_bg = "#10B981"
                icon_color = "#FFFFFF"
            elif s_id == self._current_step:
                icon = "&#9679;"
                status_class = "stage-active"
                badge = '<span style="color: #2563EB; background: #EFF6FF; border: 1px solid #BFDBFE; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 12px;">Running</span>'
                border_color = "#2563EB"
                bg_color = "#EFF6FF"
                text_color = "#1E3A8A"
                icon_bg = "#2563EB"
                icon_color = "#FFFFFF"
            else:
                icon = f"{idx}"
                status_class = "stage-pending"
                badge = '<span style="color: #64748B; background: #F8FAFC; border: 1px solid #E2E8F0; font-size: 11px; font-weight: 500; padding: 2px 8px; border-radius: 12px;">Pending</span>'
                border_color = "#E2E8F0"
                bg_color = "#FFFFFF"
                text_color = "#64748B"
                icon_bg = "#F1F5F9"
                icon_color = "#64748B"

            item = (
                f'<div style="display: flex; align-items: center; justify-content: space-between; '
                f'padding: 8px 12px; margin-bottom: 6px; border-radius: 8px; border: 1px solid {border_color}; '
                f'background: {bg_color}; transition: all 0.2s ease;">'
                f'<div style="display: flex; align-items: center; gap: 10px;">'
                f'<span style="display: inline-flex; align-items: center; justify-content: center; '
                f'width: 22px; height: 22px; border-radius: 50%; background: {icon_bg}; '
                f'font-size: 11px; font-weight: 700; color: {icon_color};">{icon}</span>'
                f'<span style="font-size: 13px; font-weight: 600; color: {text_color};">{name}</span>'
                f'</div>'
                f'<div>{badge}</div>'
                f'</div>'
            )
            items_html.append(item)

        total = len(self.STAGES)
        done = len(self._completed_steps)
        summary_bar = (
            f'<div style="margin-bottom: 12px; font-size: 12px; color: #475569; font-weight: 600;">'
            f'Pipeline Progress: {done} / {total} stages complete'
            f'</div>'
        )

        full_html = (
            f'<div style="padding: 4px 0;">'
            f'{summary_bar}'
            f'{"".join(items_html)}'
            f'</div>'
        )

        try:
            self.pipeline_placeholder.markdown(full_html, unsafe_allow_html=True)
        except Exception:
            pass

    def update(self, step_id: str, status: str) -> None:
        """Progress update callback matching actual backend stages."""
        if not self.status_box:
            return

        stage_meta = next((s for s in self.STAGES if s["id"] == step_id), None)
        friendly_name = stage_meta["name"] if stage_meta else step_id.replace("_", " ").title()

        try:
            if status == "in_progress":
                self._current_step = step_id
                self.status_box.update(
                    label=f"Active Stage: {friendly_name}...",
                    state="running",
                    expanded=True
                )
                self._render_stepper()
            elif status == "completed":
                self._completed_steps.add(step_id)
                if self._current_step == step_id:
                    self._current_step = None

                if len(self._completed_steps) >= len(self.STAGES):
                    self.status_box.update(
                        label="Validation complete — Strategic due diligence report generated.",
                        state="complete",
                        expanded=False,
                    )
                self._render_stepper()
        except Exception:
            pass
