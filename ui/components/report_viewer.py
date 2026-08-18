import os
import json
import streamlit as st
from state.schema import StartupState
from ui.components.cards import CardComponents
from ui.components.charts import ChartEngine
from tools.file_tools import FileTools
from app.config import config


def render_report_viewer(state: StartupState, session_id: str = None) -> None:
    """Renders the comprehensive validation report dashboard with clean tabs, custom cards, and download actions."""
    if not state or not state.final_report:
        st.info("No active validation report found.")
        return

    report = state.final_report
    scoring = report.scoring_breakdown
    sess_id = session_id or "session"

    # Top 3-Card Score Overview (Ring, Dimension Progress Bars, Key Insight)
    CardComponents.render_score_overview_section(state)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Validation Report Container
    st.markdown("""
<div class="saas-card report-container-card">
  <div class="saas-card-header report-header-row">
    <div>
      <div class="saas-card-label">VALIDATION REPORT</div>
      <div class="saas-title">Comprehensive Startup Validation Analysis</div>
    </div>
  </div>
""", unsafe_allow_html=True)

    # Export Action Buttons (Clean Text-Only Buttons)
    col1, col2, col3 = st.columns(3)
    
    # 1. PDF Export
    pdf_path = os.path.join(config.REPORTS_DIR, f"report_{sess_id}.pdf")
    try:
        FileTools.export_report_pdf(state, pdf_path)
    except Exception:
        pass

    pdf_bytes = b""
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as pdf_f:
                pdf_bytes = pdf_f.read()
        except Exception:
            pass

    with col1:
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"report_{sess_id}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # 2. Markdown Export
    md_path = os.path.join(config.REPORTS_DIR, f"report_{sess_id}.md")
    md_content = FileTools.export_report_markdown(state, md_path)
    with col2:
        st.download_button(
            label="Download Markdown",
            data=md_content,
            file_name=f"report_{sess_id}.md",
            mime="text/markdown",
            use_container_width=True
        )

    # 3. JSON Export
    json_str = state.model_dump_json(indent=2)
    with col3:
        st.download_button(
            label="Download JSON State",
            data=json_str,
            file_name=f"report_{sess_id}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<div class='report-tabs-divider'></div>", unsafe_allow_html=True)

    # Report Tabs
    tab_exec, tab_market, tab_comp, tab_mvp, tab_swot, tab_gtm = st.tabs([
        "Executive Summary",
        "Market Analysis",
        "Competition",
        "MVP",
        "SWOT & Risk",
        "GTM Strategy"
    ])

    with tab_exec:
        CardComponents.render_executive_summary_tab(state)

    with tab_market:
        if state.market_analysis:
            CardComponents.render_market_card(state.market_analysis)
            st.markdown('<div class="saas-card">', unsafe_allow_html=True)
            fig_growth = ChartEngine.render_market_growth_trajectory(
                state.market_analysis.tam_billions,
                state.market_analysis.cagr_percentage
            )
            st.plotly_chart(fig_growth, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_comp:
        if state.competitor_analysis:
            CardComponents.render_competitors_card(state.competitor_analysis)

    with tab_mvp:
        if state.mvp_recommendation:
            CardComponents.render_mvp_card(state.mvp_recommendation)

    with tab_swot:
        if state.swot_analysis:
            CardComponents.render_swot_risk_card(state.swot_analysis)
            st.markdown('<div class="saas-card">', unsafe_allow_html=True)
            fig_risk = ChartEngine.render_risk_severity_pie(
                state.swot_analysis.financial_risk,
                state.swot_analysis.technical_risk,
                state.swot_analysis.regulatory_risk
            )
            st.plotly_chart(fig_risk, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_gtm:
        if state.gtm_strategy:
            CardComponents.render_gtm_card(state.gtm_strategy)

    st.markdown("</div>", unsafe_allow_html=True)
