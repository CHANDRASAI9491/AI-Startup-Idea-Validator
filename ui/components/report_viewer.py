import os
import json
import streamlit as st
from state.schema import StartupState
from ui.components.cards import CardComponents
from ui.components.charts import ChartEngine
from tools.file_tools import FileTools
from app.config import config


def render_report_viewer(state: StartupState, session_id: str = None) -> None:
    """Renders the comprehensive validation report dashboard with Plotly charts and export buttons."""
    if not state or not state.final_report:
        st.info("No active validation report found.")
        return

    report = state.final_report
    scoring = report.scoring_breakdown
    sess_id = session_id or "session"

    # Export Buttons Row
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="saas-card-header"><div class="saas-title">Export Investor Report</div></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # 1. Markdown Export
    md_content = FileTools.export_report_markdown(state, os.path.join(config.REPORTS_DIR, f"report_{sess_id}.md"))
    with col1:
        st.download_button(
            label="Download Markdown (.md)",
            data=md_content,
            file_name=f"report_{sess_id}.md",
            mime="text/markdown"
        )

    # 2. JSON Export
    json_str = state.model_dump_json(indent=2)
    with col2:
        st.download_button(
            label="Download State JSON (.json)",
            data=json_str,
            file_name=f"report_{sess_id}.json",
            mime="application/json"
        )

    # 3. PDF Export
    pdf_path = os.path.join(config.REPORTS_DIR, f"report_{sess_id}.pdf")
    FileTools.export_report_pdf(state, pdf_path)
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf_f:
            pdf_bytes = pdf_f.read()
        with col3:
            st.download_button(
                label="Download PDF Report (.pdf)",
                data=pdf_bytes,
                file_name=f"report_{sess_id}.pdf",
                mime="application/pdf"
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # Executive Summary Card
    CardComponents.render_executive_summary_card(state)

    # Visual Analytics Row
    if scoring:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="saas-card-header"><div class="saas-title">Deterministic Score Matrix Analytics</div></div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            fig_bar = ChartEngine.render_scoring_matrix_bar(scoring)
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            fig_radar = ChartEngine.render_scoring_radar(scoring)
            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Market Analysis Card & Plotly Chart
    if state.market_analysis:
        CardComponents.render_market_card(state.market_analysis)
        
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        fig_growth = ChartEngine.render_market_growth_trajectory(
            state.market_analysis.tam_billions,
            state.market_analysis.cagr_percentage
        )
        st.plotly_chart(fig_growth, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Competitors Card
    if state.competitor_analysis:
        CardComponents.render_competitors_card(state.competitor_analysis)

    # SWOT & Risk Card & Pie Chart
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

    # MVP Card
    if state.mvp_recommendation:
        CardComponents.render_mvp_card(state.mvp_recommendation)

    # GTM Card
    if state.gtm_strategy:
        CardComponents.render_gtm_card(state.gtm_strategy)
