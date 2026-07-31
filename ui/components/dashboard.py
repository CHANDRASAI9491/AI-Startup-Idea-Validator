import streamlit as st
from state.schema import StartupState
from app.orchestrator import ApplicationOrchestrator
from ui.components.forms import render_startup_input_form
from ui.components.progress import ValidationProgressMonitor


def render_dashboard(orchestrator: ApplicationOrchestrator, active_state: StartupState) -> StartupState:
    """Renders main executive dashboard, input form, and validation results overview."""

    def on_form_submit(form_data: dict):
        monitor = ValidationProgressMonitor()

        def update_progress(step_id, status):
            monitor.update(step_id, status)

        with st.spinner("Executing DeepAgents and LangGraph Validation Pipeline..."):
            sess_id = st.session_state.session_id or None
            new_state = orchestrator.validate_idea(
                idea_text=form_data["idea_text"],
                startup_name=form_data["startup_name"],
                target_industry=form_data["target_industry"],
                target_audience=form_data["target_audience"],
                business_model=form_data["business_model"],
                budget=form_data["budget"],
                timeline=form_data["timeline"],
                session_id=sess_id,
                progress_callback=update_progress
            )
            st.session_state.current_state = new_state
            st.session_state.session_id = sess_id or form_data["startup_name"].replace(" ", "_")
            st.session_state.chat_history = []
            st.success("Validation complete. Navigate to 'Reports' in the sidebar or view summary below.")
            st.rerun()

    # Render input form
    render_startup_input_form(on_form_submit)

    # Active State Summary Card on Dashboard
    current_state = st.session_state.current_state or active_state
    if current_state and current_state.final_report:
        report = current_state.final_report
        idea = current_state.idea
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="saas-section-title">Current Validation Summary: {idea.startup_name}</div>', unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0 16px 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Overall Score", f"{report.overall_viability_score} / 100")
        kpi2.metric("Strategic Verdict", report.verdict)
        kpi3.metric("Market TAM", f"${current_state.market_analysis.tam_billions}B" if current_state.market_analysis else "N/A")
        kpi4.metric("Risk Level", f"{current_state.swot_analysis.overall_risk_score} / 10" if current_state.swot_analysis else "N/A")

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown(f"**Concept Description:** {idea.idea_text}")
        st.write(report.executive_summary)
        st.markdown('</div>', unsafe_allow_html=True)

    return current_state
