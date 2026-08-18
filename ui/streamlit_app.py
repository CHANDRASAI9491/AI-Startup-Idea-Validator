import os
import sys

# Ensure project root directory is at head of sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys.path[0] != root_dir:
    if root_dir in sys.path:
        sys.path.remove(root_dir)
    sys.path.insert(0, root_dir)

import streamlit as st

from app.orchestrator import ApplicationOrchestrator
from state.schema import StartupState
from app.config import config

from ui.components.styles import inject_custom_css
from ui.components.header import render_header
from ui.components.sidebar import render_sidebar
from ui.components.idea_input import render_idea_input_form
from ui.components.progress import ValidationProgressMonitor
from ui.components.report_viewer import render_report_viewer
from ui.components.advisor import render_advisor_chat
from ui.components.footer import render_footer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Development of AI Based Startup Idea Validator with Market Analysis Assistance",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_custom_css()


# ============================================================
# APPLICATION ORCHESTRATOR
# ============================================================

@st.cache_resource
def get_orchestrator():
    return ApplicationOrchestrator()


orchestrator = get_orchestrator()


# ============================================================
# SESSION STATE
# ============================================================

if "current_state" not in st.session_state:
    st.session_state.current_state = None

# Keep session_id internally because reports/orchestrator may use it.
# It is no longer displayed in the UI.
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# SIDEBAR
# ============================================================

selected_page = render_sidebar()

# Current validation state
state: StartupState = st.session_state.current_state


# ============================================================
# VALIDATE STARTUP PAGE
# ============================================================

if selected_page == "Validate Startup":

    render_header()

    def on_form_submit(form_data: dict):

        monitor = ValidationProgressMonitor()

        def update_progress(step_id, status):
            monitor.update(step_id, status)

        with st.spinner(
            "Analyzing your startup idea using the AI validation pipeline..."
        ):

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

            st.success(
                "Validation complete! View the strategic report below "
                "or open Reports from the sidebar."
            )

            st.rerun()

    # Startup Input Form
    render_idea_input_form(on_form_submit)

    # Display report after validation
    current_state = st.session_state.current_state

    if current_state and current_state.final_report:

        st.markdown(
            "<br/>",
            unsafe_allow_html=True
        )

        render_report_viewer(
            current_state,
            st.session_state.session_id
        )


# ============================================================
# REPORTS PAGE
# ============================================================

elif selected_page == "Reports":

    if not state or not state.final_report:

        st.info(
            "No active validation report found. "
            "Please validate a startup idea first."
        )

    else:

        render_report_viewer(
            state,
            st.session_state.session_id
        )


# ============================================================
# EXECUTION STATUS PAGE
# ============================================================

elif selected_page == "Execution Status":

    st.markdown(
        '<div class="saas-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="saas-card-header">
            <div class="saas-title">
                AI Agent Execution Details
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    if not state or not state.planning_output:

        st.info(
            "No active execution plan found. "
            "Please execute a startup validation first."
        )

    else:

        plan = state.planning_output
        idea = state.idea

        st.markdown(
            f"**Concept Description:** {idea.idea_text}"
        )

        st.markdown(
            f"**Strategic Objective:** {plan.strategic_objective}"
        )

        st.markdown(
            "<br/>**Strategic Research Questions:**",
            unsafe_allow_html=True
        )

        for question in plan.research_questions:
            st.markdown(f"- {question}")

        st.markdown(
            "<br/>**Agent Task Allocation:**",
            unsafe_allow_html=True
        )

        for agent_name, task in plan.agent_allocations.items():
            st.markdown(
                f"- **{agent_name}:** {task}"
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# SETTINGS PAGE
# ============================================================

elif selected_page == "Settings":

    st.markdown(
        '<div class="saas-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="saas-card-header">
            <div class="saas-title">
                Platform Configuration
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        f"**Gemini Model:** `{config.DEFAULT_MODEL}`"
    )

    st.markdown(
        "**Search Engine:** `Tavily Search API`"
    )

    st.markdown(
        f"**Maximum Search Results:** "
        f"`{config.MAX_SEARCH_RESULTS}`"
    )

    st.markdown(
        f"**Reports Directory:** "
        f"`{config.REPORTS_DIR}`"
    )

    st.markdown(
        f"**Gemini API:** "
        f"`{'Configured' if config.is_gemini_available() else 'Not Configured'}`"
    )

    st.markdown(
        f"**Tavily API:** "
        f"`{'Configured' if config.is_tavily_available() else 'Not Configured'}`"
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# ABOUT PAGE
# ============================================================

elif selected_page == "About":

    st.markdown(
        '<div class="saas-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="saas-card-header">
            <div class="saas-title">
                About Development of AI Based Startup Idea Validator with Market Analysis Assistance
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        """
The **Development of AI Based Startup Idea Validator with Market Analysis Assistance** is a multi-agent AI platform
designed to evaluate early-stage startup concepts using
real-time market research and AI-powered business analysis.

### System Architecture

- **Frontend:** Streamlit with HTML/CSS
- **Visualization:** Plotly
- **Backend:** Python
- **Multi-Agent Orchestration:** LangGraph
- **AI Language Model:** Google Gemini
- **Web Search Engine:** Tavily Search API
- **Data Validation:** Pydantic
- **Scoring:** Deterministic 8-Dimension Viability Scoring Engine
- **Reports:** PDF, Markdown and JSON

### AI Agent Pipeline

1. Planner Agent
2. Web Search Agent
3. Market Analysis Agent
4. Competitor Analysis Agent
5. SWOT & Risk Agent
6. MVP Recommendation Agent
7. Go-To-Market Strategy Agent
8. Report Generation Agent
        """
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER & FLOATING ADVISOR
# ============================================================

render_footer()

# Global floating AI Venture Advisor (accessible across all pages)
render_advisor_chat(
    orchestrator,
    state
)
