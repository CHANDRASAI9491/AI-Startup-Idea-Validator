import streamlit as st
from typing import Optional, Any
from state.schema import (
    StartupState,
    MarketAnalysis,
    CompetitorAnalysis,
    MVPRecommendation,
    SWOTAnalysis,
    GTMStrategy,
)


def _get_score_status(score: int) -> tuple[str, str]:
    """Returns status text and CSS class based on overall viability score."""
    if score >= 75:
        return "Strong", "status-strong"
    elif score >= 50:
        return "Moderate", "status-moderate"
    else:
        return "Caution", "status-caution"


def _generate_score_ring_html(score: int) -> str:
    """Generates a clean, robust CSS conic-gradient circular score ring."""
    stroke_color = "#22C55E" if score >= 75 else ("#F59E0B" if score >= 50 else "#EF4444")
    deg = int((score / 100.0) * 360)
    return (
        f'<div class="circular-score-wrapper" style="width: 88px; height: 88px; border-radius: 50%; '
        f'background: conic-gradient({stroke_color} {deg}deg, #F1F5F9 {deg}deg 360deg); '
        f'display: flex; align-items: center; justify-content: center; margin: 0.5rem auto;">'
        f'<div style="width: 72px; height: 72px; border-radius: 50%; background: #FFFFFF; '
        f'display: flex; flex-direction: column; align-items: center; justify-content: center;">'
        f'<span class="score-num" style="font-size: 1.5rem; font-weight: 800; color: #0F172A; line-height: 1;">{score}</span>'
        f'<span class="score-denom" style="font-size: 0.7rem; font-weight: 600; color: #64748B;">/ 100</span>'
        f'</div>'
        f'</div>'
    )


class CardComponents:
    """Clean, Modern SaaS HTML Card Components for Startup Validation Dashboard & Report."""

    @staticmethod
    def render_kpi_metrics_row(state: Optional[StartupState] = None) -> None:
        """Renders the top 6-card KPI metrics row (Overall Score, Market, Competition, MVP, Risk, GTM)."""
        if state and state.final_report:
            report = state.final_report
            market = state.market_analysis
            comp = state.competitor_analysis
            
            score_val = f"{report.overall_viability_score}"
            score_sub = f"Verdict: {report.verdict}"
            
            market_val = f"{report.market_score}"
            tam_str = f"TAM ${market.tam_billions:.1f}B" if (market and getattr(market, "tam_billions", None) is not None) else "Market Sizing"
            
            comp_val = f"{report.competitor_score}"
            direct_comps = getattr(comp, "direct_competitors", []) if comp else []
            comp_sub = f"{len(direct_comps)} Incumbents" if direct_comps else "Moat Assessed"
            
            mvp_val = f"{report.mvp_score}"
            mvp_sub = "Feasibility High" if report.mvp_score >= 70 else "Feasibility Moderate"
            
            risk_resilience = max(0, min(100, int((10.0 - report.risk_score) * 10)))
            risk_val = f"{risk_resilience}"
            risk_sub = f"Severity {report.risk_score}/10"
            
            gtm_val = f"{report.gtm_score}"
            gtm_sub = f"Funding {report.funding_probability}%"
        else:
            score_val = "--"
            score_sub = "Awaiting Idea"
            market_val = "--"
            tam_str = "TAM Sizing"
            comp_val = "--"
            comp_sub = "Competitive Moat"
            mvp_val = "--"
            mvp_sub = "Tech Feasibility"
            risk_val = "--"
            risk_sub = "Risk Severity"
            gtm_val = "--"
            gtm_sub = "Go-To-Market"

        html = (
            '<div class="kpi-score-cards-grid">'
            '<div class="kpi-mini-card kpi-hero">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">Viability Score</span>'
            '</div>'
            f'<div class="kpi-val-hero">{score_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{score_sub}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-market">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">Market Score</span>'
            '</div>'
            f'<div class="kpi-val-hero">{market_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{tam_str}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-comp">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">Competition</span>'
            '</div>'
            f'<div class="kpi-val-hero">{comp_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{comp_sub}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-mvp">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">MVP Readiness</span>'
            '</div>'
            f'<div class="kpi-val-hero">{mvp_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{mvp_sub}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-risk">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">Risk Resilience</span>'
            '</div>'
            f'<div class="kpi-val-hero">{risk_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{risk_sub}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-gtm">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">GTM Execution</span>'
            '</div>'
            f'<div class="kpi-val-hero">{gtm_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{gtm_sub}</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def render_dimension_progress_breakdown(state: StartupState) -> None:
        """Renders the horizontal dimension score progress bars breakdown."""
        if not state or not state.final_report:
            return

        report = state.final_report
        risk_resilience = max(0, min(100, int((10.0 - report.risk_score) * 10)))

        html = (
            '<div class="saas-card dimension-bars-card">'
            '<div class="saas-card-header" style="margin-bottom: 1rem;">'
            '<div>'
            '<div class="saas-card-label">STRATEGIC DIMENSIONS</div>'
            '<div class="saas-title" style="font-size: 1.1rem;">Dimension Score Breakdown</div>'
            '</div>'
            '</div>'
            '<div class="dimension-bars-list">'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Market Opportunity</span>'
            f'<span class="dim-bar-val">{report.market_score} / 100</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-blue" style="width: {report.market_score}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Competitive Defensibility</span>'
            f'<span class="dim-bar-val">{report.competitor_score} / 100</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-indigo" style="width: {report.competitor_score}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">MVP Feasibility</span>'
            f'<span class="dim-bar-val">{report.mvp_score} / 100</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-green" style="width: {report.mvp_score}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Risk Resilience</span>'
            f'<span class="dim-bar-val">{risk_resilience} / 100</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-orange" style="width: {risk_resilience}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Go-To-Market Execution</span>'
            f'<span class="dim-bar-val">{report.gtm_score} / 100</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-purple" style="width: {report.gtm_score}%;"></div>'
            '</div>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def render_score_overview_section(state: StartupState) -> None:
        """Renders the top 3-card score overview grid (Circular Score, Dimension Bars, Key Insight)."""
        if not state or not state.final_report:
            return

        report = state.final_report
        status_text, status_cls = _get_score_status(report.overall_viability_score)
        ring_html = _generate_score_ring_html(int(report.overall_viability_score))
        risk_resilience = max(0, min(100, int((10.0 - report.risk_score) * 10)))
        insight_text = report.key_takeaways[0] if report.key_takeaways else report.executive_summary[:200] + "..."

        html = (
            '<div class="score-overview-grid">'
            '<div class="saas-card circular-score-card">'
            '<div class="saas-card-label">OVERALL SCORE</div>'
            f'{ring_html}'
            f'<div class="score-verdict-badge {status_cls}">{status_text}</div>'
            '</div>'
            '<div class="saas-card dimension-bars-card">'
            '<div class="saas-card-label">DIMENSION SCORES</div>'
            '<div class="dimension-bars-list">'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Market</span>'
            f'<span class="dim-bar-val">{report.market_score}</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-blue" style="width: {report.market_score}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Competition</span>'
            f'<span class="dim-bar-val">{report.competitor_score}</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-indigo" style="width: {report.competitor_score}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">MVP</span>'
            f'<span class="dim-bar-val">{report.mvp_score}</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-green" style="width: {report.mvp_score}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Risk Resilience</span>'
            f'<span class="dim-bar-val">{risk_resilience}</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-orange" style="width: {risk_resilience}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">GTM</span>'
            f'<span class="dim-bar-val">{report.gtm_score}</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-purple" style="width: {report.gtm_score}%;"></div>'
            '</div>'
            '</div>'
            '</div>'
            '</div>'
            '<div class="saas-card key-insight-card">'
            '<div>'
            '<div class="saas-card-label">KEY INSIGHT</div>'
            '<div class="insight-heading">Validation Verdict</div>'
            f'<div class="insight-body">{insight_text}</div>'
            '</div>'
            f'<div class="verdict-pill verdict-proceed">{report.verdict}</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def render_executive_summary_tab(state: StartupState) -> None:
        """Renders the clean Executive Summary tab with strengths/risks cards and lower metric cards."""
        if not state or not state.final_report:
            return

        report = state.final_report
        swot = state.swot_analysis
        market = state.market_analysis
        comp = state.competitor_analysis

        strengths = getattr(swot, "strengths", [])[:4] if swot else (report.key_takeaways[:3] if report.key_takeaways else ["Strong value proposition"])
        critical_risks = getattr(swot, "threats", [])[:4] if swot else ["Early stage execution risk", "Competitive response"]

        strengths_html = "".join([f"<li>{s}</li>" for s in strengths])
        risks_html = "".join([f"<li>{r}</li>" for r in critical_risks])

        tam_val = getattr(market, "tam_billions", None) if market else None
        tam_display = f"${tam_val:.1f}B" if tam_val is not None else f"${report.market_score * 0.15:.1f}B"
        
        direct_comps = getattr(comp, "direct_competitors", []) if comp else []
        comp_count = len(direct_comps) if direct_comps else 3

        html = (
            '<div class="tab-content-container">'
            '<div class="saas-card">'
            '<div class="saas-card-label">EXECUTIVE SYNTHESIS</div>'
            '<div class="saas-title" style="font-size: 1.15rem; margin-bottom: 8px;">Executive Summary</div>'
            f'<p class="body-text">{report.executive_summary}</p>'
            '</div>'
            '<div class="two-column-cards">'
            '<div class="saas-card strengths-card">'
            '<span class="card-pill pill-green">KEY STRENGTHS</span>'
            f'<ul class="clean-bullet-list">{strengths_html}</ul>'
            '</div>'
            '<div class="saas-card risks-card">'
            '<span class="card-pill pill-red">CRITICAL RISKS</span>'
            f'<ul class="clean-bullet-list">{risks_html}</ul>'
            '</div>'
            '</div>'
            '<div class="lower-metrics-grid">'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Market Opportunity</div>'
            f'<div class="metric-hero-val">{tam_display}</div>'
            '<div class="metric-caption">Estimated TAM</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Competition</div>'
            f'<div class="metric-hero-val">{comp_count}</div>'
            '<div class="metric-caption">Direct Competitors</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">MVP Readiness</div>'
            f'<div class="metric-hero-val">{report.mvp_score}</div>'
            '<div class="metric-caption">Feasibility Score</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Funding Potential</div>'
            f'<div class="metric-hero-val">{report.funding_probability}%</div>'
            '<div class="metric-caption">Investor Probability</div>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def render_market_card(market: Any) -> None:
        """Renders the Market Analysis tab card."""
        tam = getattr(market, "tam_billions", 10.0)
        sam = getattr(market, "sam_billions", 2.5)
        som = getattr(market, "som_billions", 0.1)
        cagr = getattr(market, "cagr_percentage", 12.5)
        overview = getattr(market, "market_size_summary", "") or getattr(market, "market_overview", "")
        drivers = getattr(market, "key_growth_drivers", []) or getattr(market, "growth_drivers", [])
        personas = getattr(market, "target_personas", []) or getattr(market, "target_segments", [])

        cagr_str = f"{cagr:.1f}%" if cagr else "N/A"
        growth_html = "".join([f"<li>{g}</li>" for g in drivers]) or "<li>Growing enterprise adoption</li><li>Digital workflow transition</li>"
        
        personas_html = ""
        for p in personas:
            if hasattr(p, "role"):
                personas_html += f"<li><strong>{p.role}</strong> (WTP: {getattr(p, 'willingness_to_pay', 'Medium')})</li>"
            else:
                personas_html += f"<li>{p}</li>"
        if not personas_html:
            personas_html = "<li>Early adopters in SME segment</li>"

        html = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">MARKET INTELLIGENCE</div>'
            '<div class="saas-title">Market Opportunity &amp; Sizing</div>'
            '</div>'
            '</div>'
            '<div class="lower-metrics-grid" style="margin-top: 0; margin-bottom: 16px;">'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Total Addressable Market</div>'
            f'<div class="metric-hero-val">${tam:.1f}B</div>'
            '<div class="metric-caption">TAM Sizing</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Serviceable Addressable</div>'
            f'<div class="metric-hero-val">${sam:.1f}B</div>'
            '<div class="metric-caption">SAM Sizing</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Serviceable Obtainable</div>'
            f'<div class="metric-hero-val">${som:.2f}B</div>'
            '<div class="metric-caption">SOM Sizing</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">5-Year Growth CAGR</div>'
            f'<div class="metric-hero-val">{cagr_str}</div>'
            '<div class="metric-caption">Projected Market Growth</div>'
            '</div>'
            '</div>'
            f'<p class="body-text">{overview}</p>'
            '<div class="two-column-cards" style="margin-top: 14px;">'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">GROWTH CATALYSTS</div>'
            f'<ul class="clean-bullet-list" style="margin-top: 8px;">{growth_html}</ul>'
            '</div>'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">TARGET AUDIENCE &amp; PERSONAS</div>'
            f'<ul class="clean-bullet-list" style="margin-top: 8px;">{personas_html}</ul>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def render_competitors_card(comp: Any) -> None:
        """Renders the Competitor Analysis tab card."""
        direct = getattr(comp, "direct_competitors", [])
        competitors_html = ""
        for c in direct:
            if hasattr(c, "name"):
                desc = f": {c.description}" if getattr(c, "description", "") else ""
                competitors_html += f"<li><strong>{c.name}</strong>{desc}</li>"
            else:
                competitors_html += f"<li><strong>{c}</strong></li>"
        if not competitors_html:
            competitors_html = "<li>Identified direct incumbents in domain</li>"

        moat = getattr(comp, "moat_assessment", "") or getattr(comp, "market_positioning_summary", "") or "Defensible through specialized workflow integrations."

        html = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">COMPETITIVE MOATS</div>'
            '<div class="saas-title">Competitor Landscape &amp; Defensibility</div>'
            '</div>'
            '</div>'
            '<div class="two-column-cards">'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">DIRECT INCUMBENTS</div>'
            f'<ul class="clean-bullet-list" style="margin-top: 8px;">{competitors_html}</ul>'
            '</div>'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">MOAT &amp; POSITIONING</div>'
            f'<p class="body-text" style="margin-top: 8px;">{moat}</p>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    # Alias for compatibility
    render_competitor_card = render_competitors_card

    @staticmethod
    def render_mvp_card(mvp: Any) -> None:
        """Renders the MVP Recommendation tab card."""
        features = getattr(mvp, "features", []) or getattr(mvp, "core_features", [])
        features_html = ""
        for f in features:
            if hasattr(f, "feature_name"):
                prio = getattr(f, "priority", "Must Have")
                desc = f": {f.description}" if getattr(f, "description", "") else ""
                features_html += f"<li><strong>{f.feature_name}</strong> ({prio}){desc}</li>"
            else:
                features_html += f"<li>{f}</li>"
        if not features_html:
            features_html = "<li>Core prototype validation workflows</li>"

        fe = getattr(mvp, "tech_stack_frontend", "Streamlit / Modern CSS")
        be = getattr(mvp, "tech_stack_backend", "Python / LangGraph")
        db = getattr(mvp, "tech_stack_database", "PostgreSQL / SQLite")
        ai = getattr(mvp, "tech_stack_ai", "Google Gemini & Tavily")

        html = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">PRODUCT BLUEPRINT</div>'
            '<div class="saas-title">MVP Scope &amp; Architecture</div>'
            '</div>'
            '</div>'
            '<div class="architecture-box">'
            '<div class="arch-item">'
            '<span class="arch-label">Frontend</span>'
            f'<span class="arch-val">{fe}</span>'
            '</div>'
            '<div class="arch-item">'
            '<span class="arch-label">Backend</span>'
            f'<span class="arch-val">{be}</span>'
            '</div>'
            '<div class="arch-item">'
            '<span class="arch-label">Database</span>'
            f'<span class="arch-val">{db}</span>'
            '</div>'
            '<div class="arch-item">'
            '<span class="arch-label">AI / Services</span>'
            f'<span class="arch-val">{ai}</span>'
            '</div>'
            '</div>'
            '<div class="sub-heading">Prioritized Core Features</div>'
            f'<ul class="clean-bullet-list">{features_html}</ul>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def render_swot_risk_card(swot: Any) -> None:
        """Renders the 4-quadrant SWOT Matrix tab card."""
        str_list = getattr(swot, "strengths", [])
        weak_list = getattr(swot, "weaknesses", [])
        opp_list = getattr(swot, "opportunities", [])
        thr_list = getattr(swot, "threats", [])

        str_html = "".join([f"<li>{s}</li>" for s in str_list]) or "<li>Strong market timing</li>"
        weak_html = "".join([f"<li>{w}</li>" for w in weak_list]) or "<li>Initial brand awareness</li>"
        opp_html = "".join([f"<li>{o}</li>" for o in opp_list]) or "<li>Expansion into adjacent verticals</li>"
        thr_html = "".join([f"<li>{t}</li>" for t in thr_list]) or "<li>Competitor feature parity</li>"

        html = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">STRATEGIC MATRIX</div>'
            '<div class="saas-title">SWOT Analysis &amp; Risk Profile</div>'
            '</div>'
            '</div>'
            '<div class="swot-grid">'
            '<div class="swot-box swot-strengths">'
            '<div class="swot-header">Strengths</div>'
            f'<ul class="swot-list">{str_html}</ul>'
            '</div>'
            '<div class="swot-box swot-weaknesses">'
            '<div class="swot-header">Weaknesses</div>'
            f'<ul class="swot-list">{weak_html}</ul>'
            '</div>'
            '<div class="swot-box swot-opportunities">'
            '<div class="swot-header">Opportunities</div>'
            f'<ul class="swot-list">{opp_html}</ul>'
            '</div>'
            '<div class="swot-box swot-threats">'
            '<div class="swot-header">Threats</div>'
            f'<ul class="swot-list">{thr_html}</ul>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    # Alias for compatibility
    render_swot_card = render_swot_risk_card

    @staticmethod
    def render_gtm_card(gtm: Any) -> None:
        """Renders the Go-To-Market Strategy tab card."""
        channels = getattr(gtm, "primary_acquisition_channels", [])
        channels_html = ""
        for c in channels:
            if hasattr(c, "channel_name"):
                desc = f": {c.description}" if getattr(c, "description", "") else ""
                channels_html += f"<li><strong>{c.channel_name}</strong>{desc}</li>"
            else:
                channels_html += f"<li><strong>{c}</strong></li>"
        if not channels_html:
            channels_html = "<li>Content Marketing &amp; Developer Evangelism</li><li>Targeted Outbound to ICP</li>"

        tactics = getattr(gtm, "launch_tactics", []) or getattr(gtm, "early_adopter_tactics", [])
        tactics_html = "".join([f"<li>{t}</li>" for t in tactics]) or "<li>Beta launch with community access</li>"

        pos = getattr(gtm, "positioning_statement", "") or "The intuitive, high-velocity platform for modern teams."
        pricing = getattr(gtm, "pricing_strategy", "") or "Tiered Subscription (Freemium -> Pro -> Enterprise)"

        html = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">GROWTH ENGINE</div>'
            '<div class="saas-title">Go-To-Market Strategy</div>'
            '</div>'
            '</div>'
            '<div class="sub-heading">Strategic Positioning</div>'
            f'<p class="body-text">{pos}</p>'
            '<div class="sub-heading">Acquisition Channels</div>'
            f'<ul class="clean-bullet-list">{channels_html}</ul>'
            '<div class="two-column-cards" style="margin-top: 14px;">'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">LAUNCH TACTICS</div>'
            f'<ul class="clean-bullet-list" style="margin-top: 8px;">{tactics_html}</ul>'
            '</div>'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">PRICING STRATEGY</div>'
            f'<p class="body-text" style="margin-top: 8px;">{pricing}</p>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
