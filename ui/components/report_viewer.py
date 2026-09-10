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

    # 1. KPI Metrics Summary Cards (Viability, Market, Competitor, MVP Readiness)
    CardComponents.render_kpi_metrics_row(state)
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Top Score Overview (Score Ring, Core Dimensions, Strategic Verdict & Explanation)
    CardComponents.render_score_overview_section(state)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Key Takeaways to Results (Immediately below overall viability score)
    CardComponents.render_key_takeaways(state)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 4. Score Methodology (Dynamic read of actual ScoringBreakdown)
    CardComponents.render_score_methodology()
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 5. Real Scoring Dimensions Breakdown (Strictly bound to actual ScoringBreakdown fields)
    if scoring:
        CardComponents.render_dimension_progress_breakdown(state)
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 6. Validation Report Container Card
    st.markdown(
        '<div class="saas-card report-container-card">'
        '<div class="saas-card-header report-header-row">'
        '<div>'
        '<div class="saas-card-label">VALIDATION REPORT</div>'
        '<div class="saas-title">Comprehensive Startup Validation Analysis</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # 7. Export Action Buttons Presentation
    st.markdown('<div class="export-header-title">DOWNLOAD REPORT</div>', unsafe_allow_html=True)
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
            label="PDF",
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
            label="Markdown",
            data=md_content,
            file_name=f"report_{sess_id}.md",
            mime="text/markdown",
            use_container_width=True
        )

    # 3. JSON Export
    json_str = state.model_dump_json(indent=2)
    with col3:
        st.download_button(
            label="JSON",
            data=json_str,
            file_name=f"report_{sess_id}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<div class='report-tabs-divider'></div>", unsafe_allow_html=True)

    # 6. Report Tabs (Exact 8 Requested Sections)
    tab_exec, tab_market, tab_comp, tab_risk, tab_swot, tab_mvp, tab_gtm, tab_sources = st.tabs([
        "Executive Summary",
        "Market Opportunity",
        "Competitors",
        "Risks & Mitigation",
        "SWOT Matrix",
        "MVP Blueprint",
        "GTM Strategy",
        "Sources & Research"
    ])

    with tab_exec:
        CardComponents.render_executive_summary_tab(state)

    with tab_market:
        if state.market_analysis:
            CardComponents.render_market_card(state.market_analysis)
            st.markdown('<div class="saas-card" style="margin-top: 12px;">', unsafe_allow_html=True)
            fig_growth = ChartEngine.render_market_growth_trajectory(
                state.market_analysis.tam_billions,
                state.market_analysis.cagr_percentage
            )
            st.plotly_chart(fig_growth, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_comp:
        if state.competitor_analysis:
            CardComponents.render_competitors_card(state.competitor_analysis)

    with tab_risk:
        if state.swot_analysis:
            CardComponents.render_risk_section(state.swot_analysis)
            st.markdown('<div class="saas-card" style="margin-top: 12px;">', unsafe_allow_html=True)
            fig_risk = ChartEngine.render_risk_severity_pie(
                state.swot_analysis.financial_risk,
                state.swot_analysis.technical_risk,
                state.swot_analysis.regulatory_risk
            )
            st.plotly_chart(fig_risk, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_swot:
        if state.swot_analysis:
            CardComponents.render_swot_risk_card(state.swot_analysis)

    with tab_mvp:
        if state.mvp_recommendation:
            CardComponents.render_mvp_card(state.mvp_recommendation)

    with tab_gtm:
        if state.gtm_strategy:
            CardComponents.render_gtm_card(state.gtm_strategy)

    with tab_sources:
        CardComponents.render_sources_card(state.search_results)

    st.markdown("</div>", unsafe_allow_html=True)
