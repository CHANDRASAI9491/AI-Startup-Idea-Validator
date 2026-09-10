"""
Streamlit Application Entry Point for AI Startup Idea Validator.
Multi-Agent Startup Validation and Market Due Diligence Platform.
"""

import sys
import os
import html
import streamlit as st  # type: ignore

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.orchestrator import ApplicationOrchestrator
from state.schema import StartupState
from app.config import config
from database.chat_history import list_conversations, get_messages

from ui.components.styles import inject_custom_css
from ui.components.header import render_header, render_landing_view
from ui.components.sidebar import render_sidebar
from ui.components.idea_input import render_idea_input_form, load_example_startup_idea
from ui.components.progress import ValidationProgressMonitor
from ui.components.cards import CardComponents
from ui.components.report_viewer import render_report_viewer
from ui.components.advisor import render_advisor_chat
from ui.components.footer import render_footer

# ============================================================
# PAGE CONFIGURATION & STYLES
# ============================================================

st.set_page_config(
    page_title="AI Startup Idea Validator — SaaS Due Diligence Platform",
    page_icon="⚡",
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

if "current_page" not in st.session_state:
    st.session_state.current_page = "Validation"


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

render_sidebar()
selected_page = st.session_state.current_page
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

        st.session_state.startup_name = form_data.get("startup_name", "").strip()

        new_state = orchestrator.validate_idea(
            idea_text=form_data["idea_text"],
            target_industry=form_data.get("target_industry", "Technology / SaaS"),
            target_audience=form_data["target_audience"],
            business_model=form_data["business_model"],
            budget=form_data.get("budget", "Bootstrap ($5k - $50k)"),
            timeline=form_data["timeline"],
            session_id=sess_id,
            progress_callback=update_progress
        )

        st.session_state.current_state = new_state
        st.session_state.session_id = sess_id
        st.session_state.chat_history = []
        st.session_state.current_page = "Validation"

        st.success("Validation complete! Strategic due diligence report generated below.")
        st.rerun()


# ============================================================
# 1. VALIDATION PAGE (PRIMARY LANDING PAGE)
# ============================================================

if selected_page in ["Validation", "Validate Startup", "Dashboard"]:

    show_form = st.session_state.get("show_validation_form", False) or bool(state and state.final_report)

    if not show_form:
        def on_start():
            st.session_state.show_validation_form = True
            st.rerun()

        def on_example():
            load_example_startup_idea()
            st.rerun()

        render_landing_view(on_start_validation=on_start, on_load_example=on_example)
    else:
        render_header()
        render_idea_input_form(handle_validation_submission)

    # After Validation: Show Score Breakdown & Validation Report
    if state and state.final_report:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        render_report_viewer(state, st.session_state.session_id)


# ============================================================
# 2. HISTORY PAGE
# ============================================================

elif selected_page in ["History", "Validation History"]:

    st.markdown(
        '<div class="saas-card">'
        '<div class="saas-card-header">'
        '<div>'
        '<div class="saas-card-label">SESSION ARCHIVE &amp; LOGS</div>'
        '<div class="saas-title">Validation &amp; Advisor History</div>'
        '<div class="saas-card-subtext">Access saved due diligence reports, past validation scores, and AI Advisor conversations.</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    tab_val_hist, tab_adv_hist = st.tabs([
        "Validation History",
        "Advisor Conversations"
    ])

    with tab_val_hist:
        saved_sessions = orchestrator.list_all_sessions()
        if not saved_sessions:
            st.info("No saved validation reports found. Run a validation on the Validation page to generate your first due diligence report.")
        else:
            for s_item in saved_sessions:
                s_id = s_item.get("session_id", "session")
                s_idea = s_item.get("idea", "Startup Idea")
                s_score = s_item.get("score")
                s_verdict = s_item.get("verdict") or "EVALUATED"
                s_time = s_item.get("timestamp", "")[:19] or "Recent"

                # Truncate concept description cleanly
                disp_idea = s_idea if len(s_idea) <= 90 else s_idea[:87] + "..."

                score_badge = f'<span class="history-score-badge">{s_score}/100</span>' if s_score is not None else ""
                verdict_badge = f'<span class="verdict-pill verdict-{s_verdict.lower()}">{s_verdict}</span>' if s_verdict else ""

                col_det, col_act = st.columns([5.2, 1.4], vertical_alignment="center")
                with col_det:
                    st.markdown(
                        f'<div style="padding: 6px 0;">'
                        f'<div style="font-size: 14px; font-weight: 700; color: #0F172A;">{html.escape(disp_idea)}</div>'
                        f'<div style="font-size: 12px; color: #64748B; margin-top: 4px; display: flex; align-items: center; gap: 8px;">'
                        f'<span><strong>Session:</strong> <code>{s_id}</code></span> &bull; '
                        f'<span>{s_time}</span> &bull; '
                        f'{score_badge} {verdict_badge}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col_act:
                    if st.button("View Report", key=f"hist_view_{s_id}", use_container_width=True):
                        restored = orchestrator.get_session_history(s_id)
                        if restored:
                            st.session_state.current_state = restored
                            st.session_state.session_id = s_id
                            st.session_state.current_page = "Validation"
                            st.rerun()

                st.markdown("<div style='height: 1px; background: #E2E8F0; margin: 6px 0;'></div>", unsafe_allow_html=True)

    with tab_adv_hist:
        conversations = list_conversations()
        if not conversations:
            st.info("No saved advisor conversations found.")
        else:
            for conv in conversations:
                conv_id = conv.get("id")
                conv_title = conv.get("title", "Untitled Conversation")
                conv_sess = conv.get("session_id") or "N/A"
                conv_date = conv.get("updated_at", "")[:19] or conv.get("created_at", "")[:19]

                # Count persisted messages and get last snippet
                msgs = get_messages(conv_id)
                msg_count = len(msgs)
                last_snippet = msgs[-1]["content"][:100] + "..." if msgs else "No messages recorded."

                col_detail, col_actions = st.columns([4.8, 1.8], vertical_alignment="center")

                with col_detail:
                    st.markdown(
                        f'<div style="padding: 6px 0;">'
                        f'<div style="font-size: 14px; font-weight: 700; color: #0F172A;">{html.escape(conv_title)}</div>'
                        f'<div style="font-size: 12px; color: #475569; margin: 2px 0;">{html.escape(last_snippet)}</div>'
                        f'<div style="font-size: 11.5px; color: #64748B;">'
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
                                    st.session_state.current_page = "Validation"
                                    st.rerun()

                st.markdown("<div style='height: 1px; background: #E2E8F0; margin: 6px 0;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 3. REPORTS PAGE
# ============================================================

elif selected_page == "Reports":

    st.markdown(
        '<div class="saas-card">'
        '<div class="saas-card-header">'
        '<div>'
        '<div class="saas-card-label">REPORTS REPOSITORY</div>'
        '<div class="saas-title">Due Diligence Reports &amp; Dossiers</div>'
        '<div class="saas-card-subtext">Inspect validated startup reports from memory and disk storage.</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    saved_sessions = orchestrator.list_all_sessions()

    if saved_sessions:
        st.markdown(
            '<div style="font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 8px;">'
            'SAVED VALIDATION SESSIONS'
            '</div>',
            unsafe_allow_html=True
        )

        session_map = {}
        for s in saved_sessions:
            s_id = s.get("session_id", "session")
            s_idea = s.get("idea", "Startup Idea")
            s_score = s.get("score")
            label_text = f"{s_id} — {s_idea[:45]}... ({s_score}/100)" if s_score is not None else f"{s_id} — {s_idea[:45]}..."
            session_map[label_text] = s_id

        current_sess = st.session_state.get("session_id")
        session_keys = list(session_map.keys())
        default_idx = 0
        for idx, k in enumerate(session_keys):
            if session_map[k] == current_sess:
                default_idx = idx
                break

        selected_label = st.selectbox(
            "Select Validation Session",
            options=session_keys,
            index=default_idx,
            label_visibility="collapsed",
            key="reports_session_selector"
        )
        chosen_sess_id = session_map[selected_label]

        if chosen_sess_id != st.session_state.get("session_id"):
            restored = orchestrator.get_session_history(chosen_sess_id)
            if restored:
                st.session_state.current_state = restored
                st.session_state.session_id = chosen_sess_id
                state = restored
                st.rerun()

    if not state or not state.final_report:
        st.markdown(
            '<div style="text-align: center; padding: 2.5rem 1.5rem; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; margin-top: 12px;">'
            '<div class="saas-title" style="margin-bottom: 8px;">No Active Validation Report</div>'
            '<p style="color: #64748B; font-size: 14px; margin-bottom: 16px;">Validate a startup concept on the Validation page to review comprehensive due diligence insights.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        render_report_viewer(
            state,
            st.session_state.session_id
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 4. SETTINGS PAGE
# ============================================================

elif selected_page == "Settings":

    st.markdown(
        '<div class="saas-card">'
        '<div class="saas-card-header">'
        '<div>'
        '<div class="saas-card-label">CONFIGURATION</div>'
        '<div class="saas-title">Platform &amp; Model Parameters</div>'
        '<div class="saas-card-subtext">Safe runtime environment and service configuration metadata.</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            '<div class="saas-card" style="margin-bottom: 12px;">'
            '<div style="font-size: 12px; font-weight: 700; color: #2563EB; margin-bottom: 8px;">AI &amp; SEARCH SERVICES</div>'
            f'<div style="margin-bottom: 6px; font-size: 13px;"><strong>Gemini Model:</strong> <code>{html.escape(config.DEFAULT_MODEL)}</code></div>'
            f'<div style="margin-bottom: 6px; font-size: 13px;"><strong>Gemini API Status:</strong> <span style="color: {"#059669" if config.is_gemini_available() else "#DC2626"}; font-weight: 600;">{"Operational" if config.is_gemini_available() else "Not Configured"}</span></div>'
            f'<div style="margin-bottom: 6px; font-size: 13px;"><strong>Search Engine:</strong> <code>Tavily Intelligence API</code></div>'
            f'<div style="margin-bottom: 6px; font-size: 13px;"><strong>Tavily API Status:</strong> <span style="color: {"#059669" if config.is_tavily_available() else "#DC2626"}; font-weight: 600;">{"Operational" if config.is_tavily_available() else "Not Configured"}</span></div>'
            f'<div style="font-size: 13px;"><strong>Max Search Queries:</strong> <code>{config.MAX_SEARCH_RESULTS}</code></div>'
            '</div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            '<div class="saas-card" style="margin-bottom: 12px;">'
            '<div style="font-size: 12px; font-weight: 700; color: #2563EB; margin-bottom: 8px;">STORAGE &amp; PERSISTENCE</div>'
            f'<div style="margin-bottom: 6px; font-size: 13px;"><strong>Database Engine:</strong> <code>SQLite (chat_history.db)</code></div>'
            f'<div style="margin-bottom: 6px; font-size: 13px;"><strong>Reports Directory:</strong> <code>{html.escape(config.REPORTS_DIR)}</code></div>'
            f'<div style="margin-bottom: 6px; font-size: 13px;"><strong>State Memory Store:</strong> <code>Session MemoryStore (JSON Cache)</code></div>'
            f'<div style="font-size: 13px;"><strong>Export Formats:</strong> <code>PDF, Markdown, JSON</code></div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 5. ABOUT PAGE
# ============================================================

elif selected_page == "About":

    st.markdown(
        '<div class="saas-card">'
        '<div class="saas-card-header">'
        '<div>'
        '<div class="saas-card-label">ARCHITECTURE &amp; TECHNOLOGY</div>'
        '<div class="saas-title">AI Startup Idea Validator Platform</div>'
        '<div class="saas-card-subtext">Autonomous multi-agent due diligence framework built with LangGraph, Deep Agents, and Gemini.</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
### Enterprise AI Architecture
The **AI Startup Idea Validator** is an autonomous multi-agent due diligence system designed to evaluate early-stage venture ideas using deterministic scoring and live market intelligence.

#### Technology Stack
- **Multi-Agent Orchestration:** LangGraph state machine with Deep Agents framework
- **AI Language Model:** Google Gemini (Structured outputs & reasoning)
- **Web Intelligence:** Tavily Search API (Real-time live market & competitor research)
- **Scoring Engine:** Deterministic 8-dimension weighted model (100-point rubric)
- **Persistence:** SQLite conversation database (`chat_history.db`) & MemoryStore JSON cache
- **Frontend & Visualization:** Streamlit with custom SaaS light design system & Plotly charts
- **Dossier Exports:** Automated PDF, Markdown, and JSON state generation
""", unsafe_allow_html=True)

    st.markdown("""
### Architecture & Pipeline Flow
The authoritative validation pipeline executes sequentially across 11 discrete stages:
""", unsafe_allow_html=True)

    stages_flow = [
        ("Startup Idea", "Founder concept, industry category, ICP audience, budget, and timeline"),
        ("Planning", "Strategic decomposition, research goals, and validation hypothesis formulation"),
        ("Web Research", "Multi-query live market search via Tavily Search API for evidence retrieval"),
        ("Market Analysis", "Market sizing (TAM / SAM / SOM), projected CAGR %, and target personas"),
        ("Competitor Analysis", "Direct & indirect competitors, feature matrix, and defensibility moat"),
        ("SWOT & Risk", "4-quadrant SWOT matrix, severity-scored risk register, and mitigation plan"),
        ("MVP", "Core value proposition, Must/Should feature scope, and 4-week development roadmap"),
        ("GTM", "Primary acquisition channels, positioning statement, pricing, and CAC estimates"),
        ("Report", "Executive synthesis compiling qualitative and quantitative venture findings"),
        ("Deterministic Scoring", "Objective 8-dimension weighted algorithm computing 0–100 viability score"),
        ("Final Validation", "Complete validated dossier, strategic verdict, exports, and AI Advisor Q&A")
    ]

    flow_items = []
    for idx, (stage_title, stage_desc) in enumerate(stages_flow):
        arrow_html = '<div style="text-align: center; color: #2563EB; font-size: 16px; font-weight: 800; padding: 2px 0;">&darr;</div>' if idx < len(stages_flow) - 1 else ''
        flow_items.append(
            f'<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; margin-bottom: 2px;">'
            f'<div style="display: flex; align-items: center; justify-content: space-between;">'
            f'<span style="font-size: 13.5px; font-weight: 700; color: #0F172A;">{idx + 1}. {html.escape(stage_title)}</span>'
            f'<span style="font-size: 11px; font-weight: 600; color: #2563EB; background: #EFF6FF; border: 1px solid #DBEAFE; padding: 1px 8px; border-radius: 10px;">Active Stage</span>'
            f'</div>'
            f'<div style="font-size: 12px; color: #64748B; margin-top: 3px;">{html.escape(stage_desc)}</div>'
            f'</div>'
            f'{arrow_html}'
        )

    st.markdown(f'<div style="margin: 12px 0 20px 0;">{"".join(flow_items)}</div>', unsafe_allow_html=True)

    st.markdown("""
### Agent Roles & Responsibilities
Each autonomous agent in the system performs a dedicated function with typed data contracts:

| Agent / Module | Repository Implementation | Core Responsibility |
| :--- | :--- | :--- |
| **Strategic Planner** | `tools/planning_tool.py` (`DeepAgentsPlanner`) | Deconstructs the core problem, customer persona, and formulates structured validation hypotheses. |
| **Web Search Agent** | `tools/tavily_tool.py` (`TavilySearchTool`) | Executes 5 live query categories (trends, competitors, pain points, news, funding) via Tavily Search API. |
| **Market Analysis Agent** | `agents/market_analysis_agent.py` (`MarketAnalysisAgent`) | Evaluates TAM, SAM, SOM, CAGR %, market tailwinds, and detailed target customer personas. |
| **Competitor Agent** | `agents/competitor_agent.py` (`CompetitorAgent`) | Benchmarks direct and indirect incumbents, feature differentiation matrices, and defensibility moats. |
| **SWOT & Risk Agent** | `agents/swot_risk_agent.py` (`SWOTRiskAgent`) | Formulates a 4-quadrant SWOT matrix and a quantitative probability &times; impact risk register with mitigations. |
| **MVP Scoping Agent** | `agents/mvp_recommendation_agent.py` (`MVPRecommendationAgent`) | Scopes prioritized V1 features (Must/Should), modern tech architecture, and a 4-week execution roadmap. |
| **GTM Strategy Agent** | `agents/gtm_strategy_agent.py` (`GTMStrategyAgent`) | Identifies primary customer acquisition channels, positioning statements, pricing tiers, and estimated CAC. |
| **Report Synthesis Agent** | `agents/report_agent.py` (`ReportAgent`) | Compiles all agent findings into an executive report with strategic verdicts (PROCEED, PIVOT, CAUTION, STOP). |
| **Deterministic Scoring Engine** | `services/scoring_engine.py` (`DeterministicScoringEngine`) | Computes an objective 8-dimension weighted score (0–100) using mathematical criteria to eliminate AI variance. |
| **AI Venture Advisor** | `agents/conversational_advisor.py` (`ConversationalAdvisor`) | Interactive conversational mentor answering queries using report context, live web search, and SQLite persistence. |
""", unsafe_allow_html=True)

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
