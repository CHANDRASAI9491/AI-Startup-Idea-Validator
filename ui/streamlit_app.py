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
from ui.components.navbar import render_navbar
from ui.components.forms import render_startup_input_form
from ui.components.progress import ValidationProgressMonitor
from ui.components.cards import render_report_cards
from ui.components.advisor import render_advisor_chat
from ui.components.footer import render_footer

# Page configuration
st.set_page_config(
    page_title="AI Startup Idea Validator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Enterprise CSS
inject_custom_css()


@st.cache_resource
def get_orchestrator():
    return ApplicationOrchestrator()


orchestrator = get_orchestrator()

# Initialize session states
if "current_state" not in st.session_state:
    st.session_state.current_state = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Render Sidebar Navigation
selected_page = render_sidebar()

# Render Navbar Status
state: StartupState = st.session_state.current_state
system_status = "Operational" if state is None else (state.status.replace("_", " ").title())
render_navbar(session_id=st.session_state.session_id, status=system_status)

# PAGE ROUTING (Opens directly on Validation Page)
if selected_page == "Validate Startup":
    render_header()

    def on_form_submit(form_data: dict):
        monitor = ValidationProgressMonitor()

        def update_progress(step_id, status):
            monitor.update(step_id, status)

        with st.spinner("Executing DeepAgents and LangGraph Validation Pipeline..."):
            sess_id = st.session_state.session_id or None
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
            st.session_state.session_id = sess_id or form_data["idea_text"][:10].replace(" ", "_")
            st.session_state.chat_history = []
            st.success("Validation complete. View report summary below or navigate to 'Reports' in sidebar.")
            st.rerun()

    # Render Startup Input Form
    render_startup_input_form(on_form_submit)

    # If active validation report exists, render results below form on Validation Page
    current_state = st.session_state.current_state
    if current_state and current_state.final_report:
        st.markdown("<br/>", unsafe_allow_html=True)
        render_report_cards(current_state, st.session_state.session_id)

elif selected_page == "Reports":
    if not state or not state.final_report:
        st.info("No active validation report found. Please input a startup concept on the Validate Startup page.")
    else:
        render_report_cards(state, st.session_state.session_id)

elif selected_page == "AI Advisor":
    render_advisor_chat(orchestrator, state)

elif selected_page == "Execution Status":
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="saas-section-title">DeepAgents Execution Status Monitor</div>', unsafe_allow_html=True)
    if not state or not state.planning_output:
        st.info("No active execution plan found. Please execute a startup validation on the main page.")
    else:
        plan = state.planning_output
        idea = state.idea
        st.markdown(f"**Concept Description:** {idea.idea_text}")
        st.markdown(f"**Strategic Objective:** {plan.strategic_objective}")
        st.markdown("<br/>**Strategic Research Questions:**", unsafe_allow_html=True)
        for q in plan.research_questions:
            st.markdown(f"- {q}")
        st.markdown("<br/>**Agent Task Allocation Matrix:**", unsafe_allow_html=True)
        for agent_name, task in plan.agent_allocations.items():
            st.markdown(f"- **{agent_name}:** {task}")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "Settings":
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="saas-section-title">Platform Configuration and Engine Settings</div>', unsafe_allow_html=True)
    st.markdown(f"**Gemini Model Target:** `{config.DEFAULT_MODEL}`")
    st.markdown(f"**Max Search Results Per Category:** `{config.MAX_SEARCH_RESULTS}`")
    st.markdown(f"**Output Reports Directory:** `{config.REPORTS_DIR}`")
    st.markdown(f"**Google API Key Configured:** `{'Yes' if config.is_gemini_available() else 'No (Operating in Local Heuristic Mode)'}`")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "About":
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="saas-section-title">About Enterprise AI Startup Idea Validator</div>', unsafe_allow_html=True)
    st.markdown("""
This platform is a commercial-grade enterprise application designed to evaluate startup ideas using a multi-agent AI pipeline.

**System Architecture:**
- **UI & Visualization:** Streamlit with Plotly Charts & Vibrant SaaS Gradient Styling
- **Multi-Agent Orchestration:** DeepAgents Strategic Planner & LangGraph StateGraph
- **AI Language Model:** Google Gemini 2.5 Flash
- **Web Search Engine:** DuckDuckGo Search API
- **State Validation:** Pydantic 2.0+
- **Document Generation:** Markdown and ReportLab PDF
""")
    st.markdown('</div>', unsafe_allow_html=True)

# Render Footer
render_footer()
