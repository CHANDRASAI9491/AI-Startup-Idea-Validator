"""
Streamlit Application Entry Point for AI Startup Idea Validator.
Multi-Agent Startup Validation and Market Due Diligence Platform.
"""

import sys
import os
import streamlit as st

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.orchestrator import ApplicationOrchestrator
from state.schema import StartupState
from app.config import config
from database.chat_history import list_conversations, get_messages

from ui.components.styles import inject_custom_css
from ui.components.header import render_header, render_top_navbar
from ui.components.sidebar import render_sidebar
from ui.components.idea_input import render_idea_input_form
from ui.components.progress import ValidationProgressMonitor
from ui.components.cards import CardComponents
from ui.components.report_viewer import render_report_viewer
from ui.components.advisor import render_advisor_chat
from ui.components.footer import render_footer

# ============================================================
# PAGE CONFIGURATION & STYLES
# ============================================================

st.set_page_config(
    page_title="Development of AI Based Startup Idea Validator with Market Analysis Assistance",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

# ============================================================
# SINGLETON ORCHESTRATOR & SESSION STATE
# ============================================================

@st.cache_resource
def get_orchestrator() -> ApplicationOrchestrator:
    return ApplicationOrchestrator()

orchestrator = get_orchestrator()

if "current_state" not in st.session_state:
    st.session_state.current_state = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

selected_page = render_sidebar()
state: StartupState = st.session_state.current_state


# ============================================================
# HELPER: VALIDATION SUBMISSION HANDLER
# ============================================================

def handle_validation_submission(form_data: dict):
    """Executes multi-agent validation pipeline and stores state."""
    monitor = ValidationProgressMonitor()

    def update_progress(step_id, status):
        monitor.update(step_id, status)

    with st.spinner("Analyzing your startup idea using the AI validation pipeline..."):
        import uuid
        sess_id = st.session_state.get("session_id") or f"session_{str(uuid.uuid4())[:8]}"

        new_state = orchestrator.validate_idea(
            idea_text=form_data["idea_text"],
            target_industry=form_data["target_industry"],
            target_audience=form_data["target_audience"],
            business_model=form_data["business_model"],
            budget=form_data["budget"],
            timeline=form_data["timeline"],
            session_id=sess_id,
            progress_callback=update_progress
        )

        st.session_state.current_state = new_state
        st.session_state.session_id = sess_id
        st.session_state.chat_history = []

        st.success("Validation complete! Strategic due diligence report generated below.")
        st.rerun()


# ============================================================
# 1. VALIDATE STARTUP PAGE (PRIMARY LANDING PAGE)
# ============================================================

if selected_page == "Validate Startup" or selected_page == "Dashboard":

    render_header()

    # Startup Idea Parameters Input Form
    render_idea_input_form(handle_validation_submission)

    # After Validation: Show Score Breakdown & Validation Report
    if state and state.final_report:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        CardComponents.render_kpi_metrics_row(state)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        CardComponents.render_dimension_progress_breakdown(state)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        render_report_viewer(state, st.session_state.session_id)


# ============================================================
# 2. VALIDATION HISTORY PAGE
# ============================================================

elif selected_page == "Validation History":

    render_top_navbar()

    st.markdown(
        '<div class="saas-card">'
        '<div class="saas-card-header">'
        '<div>'
        '<div class="saas-card-label">DATABASE &amp; ADVISOR LOGS</div>'
        '<div class="saas-title">Historical Validation &amp; Advisor Sessions</div>'
        '<div class="saas-card-subtext">Access saved reports, follow-up strategic notes, and past due diligence conversations.</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    conversations = list_conversations()
    if not conversations:
        st.info("No saved validation sessions found in the database. Run a validation to create your first session.")
    else:
        for conv in conversations:
            conv_id = conv.get("id")
            conv_title = conv.get("title", "Untitled Session")
            conv_sess = conv.get("session_id") or "N/A"
            conv_date = conv.get("updated_at", "")[:19] or conv.get("created_at", "")[:19]

            # Count persisted messages
            msgs = get_messages(conv_id)
            msg_count = len(msgs)

            col_detail, col_actions = st.columns([4.8, 1.6], vertical_alignment="center")

            with col_detail:
                st.markdown(
                    f'<div style="padding: 8px 0;">'
                    f'<div style="font-size: 14px; font-weight: 700; color: #0F172A;">{conv_title}</div>'
                    f'<div style="font-size: 12px; color: #64748B; margin-top: 2px;">'
                    f'<span><strong>Session:</strong> <code>{conv_sess}</code></span> &bull; '
                    f'<span><strong>Messages:</strong> {msg_count}</span> &bull; '
                    f'<span><strong>Updated:</strong> {conv_date}</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col_actions:
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("Consult", key=f"hist_chat_{conv_id}", use_container_width=True):
                        st.session_state.active_conversation_id = conv_id
                        st.session_state.advisor_open = True
                        st.rerun()
                with col_b2:
                    if conv_sess and conv_sess != "N/A":
                        if st.button("Load", key=f"hist_load_{conv_id}", use_container_width=True):
                            restored = orchestrator.get_session_history(conv_sess)
                            if restored:
                                st.session_state.current_state = restored
                                st.session_state.session_id = conv_sess
                                st.session_state.active_conversation_id = conv_id
                                st.success("Session state restored! Navigate to Reports or Validate Startup to view.")
                                st.rerun()

            st.markdown("<div style='height: 1px; background: #E2E8F0; margin: 8px 0;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 3. REPORTS PAGE
# ============================================================

elif selected_page == "Reports":

    render_top_navbar()

    if not state or not state.final_report:
        st.markdown(
            '<div class="saas-card" style="text-align: center; padding: 2.5rem 1.5rem;">'
            '<div class="saas-title" style="margin-bottom: 8px;">No Active Validation Report</div>'
            '<p style="color: #64748B; font-size: 14px; margin-bottom: 16px;">Validate a startup concept on the Validate Startup page to review comprehensive due diligence insights.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        render_report_viewer(
            state,
            st.session_state.session_id
        )


# ============================================================
# 4. SETTINGS PAGE
# ============================================================

elif selected_page == "Settings":

    render_top_navbar()

    st.markdown(
        '<div class="saas-card">'
        '<div class="saas-card-header">'
        '<div>'
        '<div class="saas-card-label">CONFIGURATION</div>'
        '<div class="saas-title">Platform &amp; Model Parameters</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Gemini Model:** `{config.DEFAULT_MODEL}`")
        st.markdown(f"**Search Engine:** `Tavily Web Search API`")
        st.markdown(f"**Maximum Search Queries:** `{config.MAX_SEARCH_RESULTS}`")
    with c2:
        st.markdown(f"**Reports Storage:** `{config.REPORTS_DIR}`")
        st.markdown(f"**Gemini API Status:** `{'Operational' if config.is_gemini_available() else 'Not Configured'}`")
        st.markdown(f"**Tavily API Status:** `{'Operational' if config.is_tavily_available() else 'Not Configured'}`")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 5. ABOUT PAGE
# ============================================================

elif selected_page == "About":

    render_top_navbar()

    st.markdown(
        '<div class="saas-card">'
        '<div class="saas-card-header">'
        '<div>'
        '<div class="saas-card-label">ARCHITECTURE</div>'
        '<div class="saas-title">AI Startup Idea Validator Architecture</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
**AI Startup Idea Validator** is a multi-agent due diligence framework designed to evaluate early-stage venture concepts with real-time web research, market sizing, competitive analysis, risk quantification, and an interactive grounded advisor.

### System Architecture
- **Frontend:** Streamlit with Modern Custom SaaS CSS Design System
- **Visualizations:** Plotly Chart Engine &amp; Custom Indicators
- **Multi-Agent Orchestration:** LangGraph Workflow
- **AI Language Model:** Google Gemini
- **Web Intelligence:** Tavily Search API
- **Scoring Engine:** Deterministic 8-Dimension Weighted Algorithm
- **Chat Persistence:** SQLite Database
- **Export Engine:** PDF, Markdown, and JSON State

### AI Agent Pipeline
1. **Planner Agent:** Strategic research breakdown and hypothesis framing
2. **Web Search Agent:** Tavily live intelligence and evidence gathering
3. **Market Analysis Agent:** TAM / SAM / SOM calculation and growth drivers
4. **Competitor Agent:** Incumbent analysis and defensible moat identification
5. **SWOT &amp; Risk Agent:** 4-quadrant SWOT matrix and risk scoring
6. **MVP Recommendation Agent:** V1 feature prioritization and architecture stack
7. **Go-To-Market Agent:** Positioning, CAC estimation, and channel distribution
8. **Report Agent:** Executive synthesis and overall viability verdict
    """)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# FOOTER & GLOBAL FLOATING ADVISOR
# ============================================================

render_footer()

# Global floating AI Venture Advisor (accessible across all pages)
render_advisor_chat(
    orchestrator,
    state
)
