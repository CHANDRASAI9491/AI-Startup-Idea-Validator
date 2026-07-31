import os
import json
import streamlit as st
from state.schema import StartupState
from tools.file_tools import FileTools
from app.config import config
from ui.components.charts import (
    render_startup_score_gauge,
    render_8dimension_score_breakdown_chart,
    render_market_growth_line_chart,
    render_swot_radar_chart,
    render_risk_distribution_pie_chart,
    render_competitor_comparison_chart
)


def render_report_cards(state: StartupState, session_id: str):
    """Renders modular enterprise validation report cards."""
    report = state.final_report
    idea = state.idea
    market = state.market_analysis
    comp = state.competitor_analysis
    swot = state.swot_analysis
    mvp = state.mvp_recommendation
    gtm = state.gtm_strategy
    scoring = report.scoring_breakdown if report else None

    if not report:
        st.info("No completed validation report available.")
        return

    # CARD 1: Executive Summary, Startup Description Panel & Viability Gauge
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="saas-section-title">Executive Decision Support & Investor Metrics</div>', unsafe_allow_html=True)
    st.markdown("<hr style='margin: 8px 0 16px 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.2, 1.2, 2.6])
    with col1:
        st.metric("Overall Viability Index", f"{report.overall_viability_score} / 100")
        verdict_cls = "verdict-proceed" if report.verdict == "PROCEED" else ("verdict-pivot" if report.verdict in ["PIVOT", "CAUTION"] else "verdict-caution")
        st.markdown(f'<div class="verdict-badge {verdict_cls}" style="margin-top: 8px;">{report.verdict}</div>', unsafe_allow_html=True)
    with col2:
        fig_gauge = render_startup_score_gauge(report.overall_viability_score, report.verdict)
        st.plotly_chart(fig_gauge, use_container_width=True)
    with col3:
        st.markdown(f"**Startup Description:** {idea.idea_text}")
        st.markdown(f"**Industry Sector:** {idea.target_industry} | **Target Audience:** {idea.target_audience}")
        st.markdown(f"**Business Model:** {idea.business_model}")

    st.markdown("<br/>", unsafe_allow_html=True)

    # Investor Decision Support KPI Grid
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Investor Readiness", f"{report.investor_readiness_score} / 100")
    kpi2.metric("Funding Probability", f"{report.funding_probability}%")
    kpi3.metric("PMF Score", f"{report.pmf_score} / 100")
    kpi4.metric("Confidence Level", f"{report.confidence_score}%")
    kpi5.metric("Market TAM", f"${market.tam_billions}B" if market else "N/A")

    st.markdown("<br/>", unsafe_allow_html=True)
    st.write(report.executive_summary)

    # Render 8-Dimension Deterministic Score Matrix Chart
    if scoring:
        fig_matrix = render_8dimension_score_breakdown_chart(scoring)
        st.plotly_chart(fig_matrix, use_container_width=True)

        with st.expander("Explainable Reasoning & Score Drivers (WHY)", expanded=True):
            st.markdown("**Evidence-Based Scoring Drivers:**")
            for r in scoring.reasoning_why:
                st.markdown(f"- {r}")

    with st.expander("Executive Takeaways and Strategic Recommendations", expanded=False):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("**Key Takeaways:**")
            for t in report.key_takeaways:
                st.markdown(f"- {t}")
        with col_t2:
            st.markdown("**Recommended Next Steps:**")
            for i, step in enumerate(report.recommended_next_steps, 1):
                st.markdown(f"{i}. {step}")

    st.markdown('</div>', unsafe_allow_html=True)

    # CARD 2: Market Analysis & Growth Trajectory
    if market:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="saas-section-title">Market Analysis & Growth Trajectory</div>', unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0 16px 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("TAM (Total Addressable)", f"${market.tam_billions}B")
        m_col2.metric("SAM (Serviceable)", f"${market.sam_billions}B")
        m_col3.metric("SOM (Obtainable)", f"${market.som_billions}B")
        m_col4.metric("Market CAGR %", f"{market.cagr_percentage}%")

        fig_line = render_market_growth_line_chart(market.tam_billions, market.sam_billions, market.som_billions, market.cagr_percentage)
        st.plotly_chart(fig_line, use_container_width=True)

        st.write(market.market_size_summary)

        with st.expander("Target Customer Personas and Growth Drivers", expanded=False):
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("**Primary Growth Drivers:**")
                for d in market.key_growth_drivers:
                    st.markdown(f"- {d}")
            with col_g2:
                st.markdown("**Target Customer Personas:**")
                for persona in market.target_personas:
                    st.markdown(f"- **Role:** {persona.role} (Pay: {persona.willingness_to_pay})")
                    st.markdown(f"  Pain Points: {', '.join(persona.pain_points)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # CARD 3: Competitor Analysis & Moat Mapping
    if comp:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="saas-section-title">Competitor Intelligence & Moat Mapping</div>', unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0 16px 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

        st.markdown(f"**Market Positioning:** {comp.market_positioning_summary}")
        st.markdown(f"**Defensible Moat:** {comp.moat_assessment}")

        comp_names = [c.name for c in comp.direct_competitors] or ["Incumbent A", "Incumbent B"]
        comp_strengths = [len(c.strengths) for c in comp.direct_competitors] or [3, 2]
        fig_comp = render_competitor_comparison_chart(comp_names, comp_strengths)
        st.plotly_chart(fig_comp, use_container_width=True)

        with st.expander("Direct Incumbents Matrix & Indirect Competitors", expanded=True):
            for competitor in comp.direct_competitors:
                st.markdown(f"**{competitor.name}** ({competitor.pricing_model})")
                st.write(competitor.description)
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown("**Strengths:** " + ", ".join(competitor.strengths))
                with col_c2:
                    st.markdown("**Weaknesses:** " + ", ".join(competitor.weaknesses))

        st.markdown('</div>', unsafe_allow_html=True)

    # CARD 4: SWOT & Risk Assessment
    if swot:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="saas-section-title">SWOT Matrix & Risk Severity Pie Chart</div>', unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0 16px 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        r_col1.metric("Financial Risk", f"{swot.financial_risk} / 10")
        r_col2.metric("Technical Risk", f"{swot.technical_risk} / 10")
        r_col3.metric("Regulatory Risk", f"{swot.regulatory_risk} / 10")
        r_col4.metric("Overall Risk Score", f"{swot.overall_risk_score} / 10")

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            fig_swot = render_swot_radar_chart(
                len(swot.strengths), len(swot.opportunities), len(swot.threats), len(swot.weaknesses)
            )
            st.plotly_chart(fig_swot, use_container_width=True)
        with col_w2:
            fig_pie = render_risk_distribution_pie_chart(
                swot.financial_risk, swot.technical_risk, swot.regulatory_risk
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with st.expander("SWOT Factors and Risk Mitigation Plan", expanded=False):
            col_sw1, col_sw2 = st.columns(2)
            with col_sw1:
                st.markdown("**Strengths:** " + ", ".join(swot.strengths))
                st.markdown("**Opportunities:** " + ", ".join(swot.opportunities))
            with col_sw2:
                st.markdown("**Weaknesses:** " + ", ".join(swot.weaknesses))
                st.markdown("**Threats:** " + ", ".join(swot.threats))

            st.markdown("<br/>**Risk Mitigation Plan:**", unsafe_allow_html=True)
            for plan in swot.risk_mitigation_plan:
                st.markdown(f"- {plan}")

        st.markdown('</div>', unsafe_allow_html=True)

    # CARD 5: MVP Roadmap & Tech Stack
    if mvp:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="saas-section-title">MVP Feature Scope & Technology Architecture</div>', unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0 16px 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

        st.markdown(f"**Core Value Proposition:** {mvp.core_value_proposition}")
        st.markdown(f"**Recommended Stack:** Frontend (`{mvp.tech_stack_frontend}`), Backend (`{mvp.tech_stack_backend}`), Database (`{mvp.tech_stack_database}`), AI (`{mvp.tech_stack_ai}`)")

        with st.expander("Four-Week Development Roadmap & Feature Scope", expanded=True):
            for week, desc in mvp.four_week_roadmap.items():
                st.markdown(f"- **{week}:** {desc}")

        st.markdown('</div>', unsafe_allow_html=True)

    # CARD 6: Go-To-Market Strategy
    if gtm:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="saas-section-title">Go-To-Market (GTM) Strategy & Acquisition</div>', unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0 16px 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

        st.markdown(f"**Positioning Statement:** {gtm.positioning_statement}")
        st.markdown(f"**Pricing Strategy:** {gtm.pricing_strategy}")
        st.markdown(f"**CAC Estimate:** {gtm.estimated_cac_summary}")

        with st.expander("Primary Acquisition Channels & Launch Tactics", expanded=False):
            st.markdown("**Channels:** " + ", ".join(gtm.primary_acquisition_channels))
            for tactic in gtm.launch_tactics:
                st.markdown(f"- {tactic}")

        st.markdown('</div>', unsafe_allow_html=True)

    # CARD 7: Export Options & Downloads
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="saas-section-title">Download Validation Reports</div>', unsafe_allow_html=True)
    st.markdown("<hr style='margin: 8px 0 16px 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    col_d1, col_d2, col_d3, col_d4 = st.columns(4)

    # Markdown Download
    md_content = FileTools.export_report_markdown(state, os.path.join(config.REPORTS_DIR, "temp_report.md"))
    col_d1.download_button(
        label="Download Markdown",
        data=md_content,
        file_name=f"validation_report_{session_id}.md",
        mime="text/markdown",
        use_container_width=True
    )

    # JSON Download
    json_content = state.model_dump_json(indent=2)
    col_d2.download_button(
        label="Download JSON",
        data=json_content,
        file_name=f"validation_report_{session_id}.json",
        mime="application/json",
        use_container_width=True
    )

    # PDF Download
    pdf_path = os.path.join(config.REPORTS_DIR, f"report_{session_id}.pdf")
    gen_pdf = FileTools.export_report_pdf(state, pdf_path)
    if gen_pdf and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        col_d3.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"validation_report_{session_id}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # Print View Button
    if col_d4.button("Print Report View", use_container_width=True):
        st.info("To print this report, use browser print shortcut (Ctrl+P / Cmd+P).")

    st.markdown('</div>', unsafe_allow_html=True)
