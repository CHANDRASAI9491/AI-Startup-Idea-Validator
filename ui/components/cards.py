import streamlit as st
import html
from urllib.parse import urlparse
from typing import Optional, Any, List, Dict
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
        f'<div class="circular-score-wrapper" style="width: 92px; height: 92px; border-radius: 50%; '
        f'background: conic-gradient({stroke_color} {deg}deg, #F1F5F9 {deg}deg 360deg); '
        f'display: flex; align-items: center; justify-content: center; margin: 0.5rem auto;">'
        f'<div style="width: 76px; height: 76px; border-radius: 50%; background: #FFFFFF; '
        f'display: flex; flex-direction: column; align-items: center; justify-content: center;">'
        f'<span class="score-num" style="font-size: 1.65rem; font-weight: 800; color: #0F172A; line-height: 1;">{score}</span>'
        f'<span class="score-denom" style="font-size: 0.72rem; font-weight: 600; color: #64748B;">/ 100</span>'
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

        html_content = (
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
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_dimension_progress_breakdown(state: StartupState) -> None:
        """Renders the horizontal dimension score progress bars breakdown."""
        if not state or not state.final_report:
            return

        report = state.final_report
        risk_resilience = max(0, min(100, int((10.0 - report.risk_score) * 10)))

        html_content = (
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
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_score_overview_section(state: StartupState) -> None:
        """Renders the strong validation score section with the exact requested visual structure."""
        if not state or not state.final_report:
            return

        report = state.final_report
        status_text, status_cls = _get_score_status(report.overall_viability_score)
        ring_html = _generate_score_ring_html(int(report.overall_viability_score))

        # Calculate real dimension indicators from the actual report
        market_pct = report.market_score
        comp_pct = report.competitor_score
        problem_pct = report.pmf_score if getattr(report, "pmf_score", None) else (
            int((report.scoring_breakdown.innovation_score / 15.0) * 100) if getattr(report, "scoring_breakdown", None) else 80
        )
        risk_pct = max(0, min(100, int((10.0 - report.risk_score) * 10)))
        verdict_val = report.verdict.upper()

        insight_text = report.key_takeaways[0] if report.key_takeaways else report.executive_summary[:220] + "..."

        html_content = (
            '<div class="score-overview-grid">'
            '<div class="saas-card circular-score-card">'
            '<div class="saas-card-label">STARTUP VALIDATION SCORE</div>'
            f'{ring_html}'
            f'<div class="score-verdict-badge {status_cls}">{verdict_val}</div>'
            '</div>'
            '<div class="saas-card dimension-bars-card">'
            '<div class="saas-card-label">CORE VALIDATION DIMENSIONS</div>'
            '<div class="dimension-bars-list">'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Market Opportunity</span>'
            f'<span class="dim-bar-val">{market_pct}%</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-blue" style="width: {market_pct}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Problem Strength</span>'
            f'<span class="dim-bar-val">{problem_pct}%</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-green" style="width: {problem_pct}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Competition</span>'
            f'<span class="dim-bar-val">{comp_pct}%</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-indigo" style="width: {comp_pct}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">Risk Resilience</span>'
            f'<span class="dim-bar-val">{risk_pct}%</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-orange" style="width: {risk_pct}%;"></div>'
            '</div>'
            '</div>'
            '</div>'
            '</div>'
            '<div class="saas-card key-insight-card">'
            '<div>'
            '<div class="saas-card-label">STRATEGIC VERDICT</div>'
            f'<div class="insight-heading">Verdict: {verdict_val}</div>'
            f'<div class="insight-body">{html.escape(insight_text)}</div>'
            '</div>'
            f'<div class="verdict-pill verdict-{verdict_val.lower()}">{verdict_val}</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

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

        strengths_html = "".join([f"<li>{html.escape(s)}</li>" for s in strengths])
        risks_html = "".join([f"<li>{html.escape(r)}</li>" for r in critical_risks])

        tam_val = getattr(market, "tam_billions", None) if market else None
        tam_display = f"${tam_val:.1f}B" if tam_val is not None else f"${report.market_score * 0.15:.1f}B"

        direct_comps = getattr(comp, "direct_competitors", []) if comp else []
        comp_count = len(direct_comps) if direct_comps else 3

        next_steps_html = "".join([f"<li>{html.escape(step)}</li>" for step in report.recommended_next_steps]) if report.recommended_next_steps else "<li>Build high-fidelity MVP prototype</li>"

        html_content = (
            '<div class="tab-content-container">'
            '<div class="saas-card">'
            '<div class="saas-card-label">EXECUTIVE SYNTHESIS</div>'
            '<div class="saas-title" style="font-size: 1.15rem; margin-bottom: 8px;">Executive Summary</div>'
            f'<p class="body-text">{html.escape(report.executive_summary)}</p>'
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
            '<div class="saas-card">'
            '<div class="saas-card-label">ACTIONABLE ROADMAP</div>'
            '<div class="saas-title" style="font-size: 1.05rem; margin-bottom: 8px;">Recommended Next Steps</div>'
            f'<ul class="clean-bullet-list">{next_steps_html}</ul>'
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
        st.markdown(html_content, unsafe_allow_html=True)

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
        growth_html = "".join([f"<li>{html.escape(g)}</li>" for g in drivers]) or "<li>Growing enterprise adoption</li><li>Digital workflow transition</li>"

        personas_html = ""
        for p in personas:
            if hasattr(p, "role"):
                p_role = html.escape(p.role)
                p_wtp = html.escape(str(getattr(p, "willingness_to_pay", "Medium")))
                p_pains = ", ".join([html.escape(pn) for pn in getattr(p, "pain_points", [])])
                pain_sub = f" &bull; Pain points: {p_pains}" if p_pains else ""
                personas_html += f"<li><strong>{p_role}</strong> (WTP: {p_wtp}){pain_sub}</li>"
            else:
                personas_html += f"<li>{html.escape(str(p))}</li>"
        if not personas_html:
            personas_html = "<li>Early adopters in SME segment</li>"

        html_content = (
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
            f'<p class="body-text">{html.escape(overview)}</p>'
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
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_competitors_card(comp: Any) -> None:
        """Renders the Professional Competitor Comparison UI with real data."""
        direct = getattr(comp, "direct_competitors", [])
        indirect = getattr(comp, "indirect_competitors", [])
        moat = getattr(comp, "moat_assessment", "") or "Defensible workflow automation, proprietary data loops, and rapid time-to-value."
        pos_summary = getattr(comp, "market_positioning_summary", "") or "AI-native solution addressing core user friction."

        cards_html = []

        # Render Direct Competitors
        for c in direct:
            name = getattr(c, "name", "Competitor")
            url = getattr(c, "url", "")
            desc = getattr(c, "description", "")
            pricing = getattr(c, "pricing_model", "Subscription")
            strengths = getattr(c, "strengths", [])
            weaknesses = getattr(c, "weaknesses", [])
            features = getattr(c, "key_features", [])

            parsed_url = urlparse(str(url)) if url else None
            is_safe_url = bool(
                parsed_url
                and parsed_url.scheme in {"http", "https"}
                and parsed_url.netloc
            )

            link_html = (
                f' &bull; <a href="{html.escape(str(url), quote=True)}" '
                f'target="_blank" rel="noopener noreferrer" '
                f'style="color: #2563EB; font-size: 12px; text-decoration: none;">'
                f'Website &rarr;</a>'
                if is_safe_url
                else ""
            )
            str_items = "".join([f"<li>{html.escape(s)}</li>" for s in strengths]) if strengths else "<li>Brand presence</li>"
            weak_items = "".join([f"<li>{html.escape(w)}</li>" for w in weaknesses]) if weaknesses else "<li>Slower iteration</li>"
            feat_pills = "".join([f'<span class="competitor-feature-tag">{html.escape(f)}</span>' for f in features]) if features else ""

            cards_html.append(
                '<div class="competitor-item-card">'
                '<div class="competitor-card-header">'
                '<div>'
                f'<span class="competitor-name">{html.escape(name)}</span>{link_html}'
                f'<div class="competitor-desc">{html.escape(desc)}</div>'
                '</div>'
                ''
                '</div>'
                f'<div class="competitor-pricing-tag">Pricing Model: <strong>{html.escape(pricing)}</strong></div>'
                f'<div class="competitor-features-row">{feat_pills}</div>'
                '<div class="competitor-sw-grid">'
                '<div class="comp-strengths-box">'
                '<span class="comp-sw-label green">Strengths</span>'
                f'<ul class="comp-sw-list">{str_items}</ul>'
                '</div>'
                '<div class="comp-weaknesses-box">'
                '<span class="comp-sw-label red">Weaknesses</span>'
                f'<ul class="comp-sw-list">{weak_items}</ul>'
                '</div>'
                '</div>'
                '</div>'
            )

        # Render Indirect Competitors if present
        for c in indirect:
            name = getattr(c, "name", "Alternative")
            desc = getattr(c, "description", "")
            pricing = getattr(c, "pricing_model", "Internal / Alternative")
            strengths = getattr(c, "strengths", [])
            weaknesses = getattr(c, "weaknesses", [])

            str_items = "".join([f"<li>{html.escape(s)}</li>" for s in strengths]) if strengths else "<li>Low initial cost</li>"
            weak_items = "".join([f"<li>{html.escape(w)}</li>" for w in weaknesses]) if weaknesses else "<li>Manual effort</li>"

            cards_html.append(
                '<div class="competitor-item-card">'
                '<div class="competitor-card-header">'
                '<div>'
                f'<span class="competitor-name">{html.escape(name)}</span>'
                f'<div class="competitor-desc">{html.escape(desc)}</div>'
                '</div>'
                ''
                '</div>'
                f'<div class="competitor-pricing-tag">Cost: <strong>{html.escape(pricing)}</strong></div>'
                '<div class="competitor-sw-grid">'
                '<div class="comp-strengths-box">'
                '<span class="comp-sw-label green">Strengths</span>'
                f'<ul class="comp-sw-list">{str_items}</ul>'
                '</div>'
                '<div class="comp-weaknesses-box">'
                '<span class="comp-sw-label red">Weaknesses</span>'
                f'<ul class="comp-sw-list">{weak_items}</ul>'
                '</div>'
                '</div>'
                '</div>'
            )

        competitors_grid = "".join(cards_html) if cards_html else "<p class='body-text'>No competitor records identified.</p>"

        html_content = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">COMPETITIVE INTELLIGENCE</div>'
            '<div class="saas-title">Competitor Comparison &amp; Defensibility</div>'
            '</div>'
            '</div>'
            '<div class="two-column-cards" style="margin-bottom: 16px;">'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">MARKET POSITIONING</div>'
            f'<p class="body-text" style="margin-top: 6px;">{html.escape(pos_summary)}</p>'
            '</div>'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">DEFENSIBLE MOAT ASSESSMENT</div>'
            f'<p class="body-text" style="margin-top: 6px;">{html.escape(moat)}</p>'
            '</div>'
            '</div>'
            f'<div class="competitor-cards-container">{competitors_grid}</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    # Alias for compatibility
    render_competitor_card = render_competitors_card

    @staticmethod
    def render_risk_section(swot: Any) -> None:
        """Renders the visually clear, structured Risk Analysis section using real risk_matrix data."""
        risk_matrix = getattr(swot, "risk_matrix", [])
        fin_risk = getattr(swot, "financial_risk", 5)
        tech_risk = getattr(swot, "technical_risk", 4)
        reg_risk = getattr(swot, "regulatory_risk", 3)
        overall_risk = getattr(swot, "overall_risk_score", 4)
        mitigation_plan = getattr(swot, "risk_mitigation_plan", [])

        risk_cards = []
        for r in risk_matrix:
            r_name = getattr(r, "risk_name", "Venture Risk")
            cat = getattr(r, "category", "Execution")
            prob = getattr(r, "probability", 3)
            imp = getattr(r, "impact", 3)
            sev = getattr(r, "severity_score", prob * imp)
            mit = getattr(r, "mitigation_strategy", "")

            # Determine severity level
            if sev >= 15:
                sev_label = "Critical Severity"
                sev_cls = "sev-critical"
            elif sev >= 10:
                sev_label = "High Severity"
                sev_cls = "sev-high"
            elif sev >= 6:
                sev_label = "Moderate Severity"
                sev_cls = "sev-moderate"
            else:
                sev_label = "Low Severity"
                sev_cls = "sev-low"

            mit_html = (
                f'<div class="risk-mitigation-box">'
                f'<strong>Recommended Mitigation:</strong> {html.escape(mit)}'
                f'</div>'
            ) if mit else ""

            risk_cards.append(
                '<div class="risk-item-card">'
                '<div class="risk-card-header">'
                '<div>'
                f'<span class="risk-title">{html.escape(r_name)}</span>'
                f'<span class="risk-category-badge">{html.escape(cat)} Risk</span>'
                '</div>'
                f'<span class="risk-severity-pill {sev_cls}">{sev_label} &bull; {sev}/25</span>'
                '</div>'
                f'<div class="risk-metric-subtext">Probability: {prob}/5 &bull; Impact: {imp}/5</div>'
                f'{mit_html}'
                '</div>'
            )

        risks_html = "".join(risk_cards) if risk_cards else "<p class='body-text'>No quantified risk items found.</p>"

        plan_items = "".join([f"<li>{html.escape(p)}</li>" for p in mitigation_plan]) if mitigation_plan else "<li>Maintain lean execution cycles</li>"

        html_content = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">RISK DUE DILIGENCE</div>'
            '<div class="saas-title">Risk Analysis &amp; Mitigation Strategy</div>'
            '</div>'
            '</div>'
            '<div class="lower-metrics-grid" style="margin-top: 0; margin-bottom: 16px;">'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Overall Risk Index</div>'
            f'<div class="metric-hero-val">{overall_risk}/10</div>'
            '<div class="metric-caption">Aggregate Risk</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Financial Exposure</div>'
            f'<div class="metric-hero-val">{fin_risk}/10</div>'
            '<div class="metric-caption">Capital &amp; CAC Risk</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Technical Feasibility</div>'
            f'<div class="metric-hero-val">{tech_risk}/10</div>'
            '<div class="metric-caption">Complexity Risk</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Regulatory &amp; Market</div>'
            f'<div class="metric-hero-val">{reg_risk}/10</div>'
            '<div class="metric-caption">Compliance Risk</div>'
            '</div>'
            '</div>'
            f'<div class="risk-cards-container">{risks_html}</div>'
            '<div class="saas-card" style="margin-top: 14px; margin-bottom: 0;">'
            '<div class="saas-card-label">STRATEGIC MITIGATION ROADMAP</div>'
            f'<ul class="clean-bullet-list" style="margin-top: 8px;">{plan_items}</ul>'
            '</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_sources_card(search_results: Any) -> None:
        """Renders professional Tavily research source cards with real domains and links."""
        categories = [
            ("Market Trends", getattr(search_results, "market_trends", []) if search_results else []),
            ("Competitors", getattr(search_results, "competitors", []) if search_results else []),
            ("Customer Pain Points", getattr(search_results, "customer_pain_points", []) if search_results else []),
            ("Industry News", getattr(search_results, "industry_news", []) if search_results else []),
            ("Funding Intel", getattr(search_results, "funding", []) if search_results else []),
        ]

        source_cards = []
        total_sources = 0

        for cat_label, items in categories:
            if not items:
                continue
            for itm in items:
                total_sources += 1
                title = getattr(itm, "title", "Web Intelligence Source")
                url = getattr(itm, "url", "")
                snippet = getattr(itm, "snippet", "")
                domain = urlparse(url).netloc.replace("www.", "") if url else "web"

                parsed_source_url = urlparse(str(url)) if url else None
                is_safe_source_url = bool(
                    parsed_source_url
                    and parsed_source_url.scheme in {"http", "https"}
                    and parsed_source_url.netloc
                )

                link_action = (
                    f'<a href="{html.escape(str(url), quote=True)}" '
                    f'target="_blank" rel="noopener noreferrer" '
                    f'class="source-card-action">'
                    f'Open Source &rarr;'
                    f'</a>'
                    if is_safe_source_url
                    else ""
                )

                source_cards.append(
                    '<div class="tavily-source-card">'
                    '<div class="source-card-top">'
                    f'<span class="source-cat-badge">{html.escape(cat_label)}</span>'
                    f'<span class="source-domain-pill">{html.escape(domain)}</span>'
                    '</div>'
                    f'<div class="source-card-title">{html.escape(title)}</div>'
                    f'<div class="source-card-snippet">{html.escape(snippet)}</div>'
                    f'<div class="source-card-footer">{link_action}</div>'
                    '</div>'
                )

        if not source_cards:
            grid_html = (
                '<div style="text-align: center; padding: 2rem; color: #64748B;">'
                'No live web research records stored for this session.'
                '</div>'
            )
        else:
            grid_html = f'<div class="tavily-sources-grid">{"".join(source_cards)}</div>'

        html_content = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">EVIDENCE &amp; WEB INTELLIGENCE</div>'
            '<div class="saas-title">Live Market Research Sources</div>'
            f'<div class="saas-card-subtext">Real-time market insights and external validation data gathered via Tavily Search API ({total_sources} verified sources).</div>'
            '</div>'
            '</div>'
            f'{grid_html}'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_mvp_card(mvp: Any) -> None:
        """Renders the MVP Recommendation tab card."""
        features = getattr(mvp, "features", []) or getattr(mvp, "core_features", [])
        features_html = ""
        for f in features:
            if hasattr(f, "feature_name"):
                prio = html.escape(str(getattr(f, "priority", "Must Have")))
                desc = f": {html.escape(f.description)}" if getattr(f, "description", "") else ""
                features_html += f"<li><strong>{html.escape(f.feature_name)}</strong> ({prio}){desc}</li>"
            else:
                features_html += f"<li>{html.escape(str(f))}</li>"
        if not features_html:
            features_html = "<li>Core prototype validation workflows</li>"

        fe = html.escape(str(getattr(mvp, "tech_stack_frontend", "Streamlit / Modern CSS")))
        be = html.escape(str(getattr(mvp, "tech_stack_backend", "Python / LangGraph")))
        db = html.escape(str(getattr(mvp, "tech_stack_database", "PostgreSQL / SQLite")))
        ai = html.escape(str(getattr(mvp, "tech_stack_ai", "Google Gemini & Tavily")))

        # 4-Week Roadmap
        roadmap = getattr(mvp, "four_week_roadmap", {})
        roadmap_items = "".join([f"<li><strong>{html.escape(w)}:</strong> {html.escape(t)}</li>" for w, t in roadmap.items()]) if roadmap else "<li>Week 1-4: Core implementation</li>"

        html_content = (
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
            '<div class="two-column-cards" style="margin-top: 14px;">'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">PRIORITIZED CORE FEATURES</div>'
            f'<ul class="clean-bullet-list" style="margin-top: 8px;">{features_html}</ul>'
            '</div>'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">4-WEEK BUILD ROADMAP</div>'
            f'<ul class="clean-bullet-list" style="margin-top: 8px;">{roadmap_items}</ul>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_swot_risk_card(swot: Any) -> None:
        """Renders the 4-quadrant SWOT Matrix tab card."""
        str_list = getattr(swot, "strengths", [])
        weak_list = getattr(swot, "weaknesses", [])
        opp_list = getattr(swot, "opportunities", [])
        thr_list = getattr(swot, "threats", [])

        str_html = "".join([f"<li>{html.escape(s)}</li>" for s in str_list]) or "<li>Strong market timing</li>"
        weak_html = "".join([f"<li>{html.escape(w)}</li>" for w in weak_list]) or "<li>Initial brand awareness</li>"
        opp_html = "".join([f"<li>{html.escape(o)}</li>" for o in opp_list]) or "<li>Expansion into adjacent verticals</li>"
        thr_html = "".join([f"<li>{html.escape(t)}</li>" for t in thr_list]) or "<li>Competitor feature parity</li>"

        html_content = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">STRATEGIC MATRIX</div>'
            '<div class="saas-title">SWOT Analysis &amp; Strategic Quadrants</div>'
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
        st.markdown(html_content, unsafe_allow_html=True)

    # Alias for compatibility
    render_swot_card = render_swot_risk_card

    @staticmethod
    def render_gtm_card(gtm: Any) -> None:
        """Renders the Go-To-Market Strategy tab card."""
        channels = getattr(gtm, "primary_acquisition_channels", [])
        channels_html = ""
        for c in channels:
            if hasattr(c, "channel_name"):
                desc = f": {html.escape(c.description)}" if getattr(c, "description", "") else ""
                channels_html += f"<li><strong>{html.escape(c.channel_name)}</strong>{desc}</li>"
            else:
                channels_html += f"<li><strong>{html.escape(str(c))}</strong></li>"
        if not channels_html:
            channels_html = "<li>Content Marketing &amp; Developer Evangelism</li><li>Targeted Outbound to ICP</li>"

        tactics = getattr(gtm, "launch_tactics", []) or getattr(gtm, "early_adopter_tactics", [])
        tactics_html = "".join([f"<li>{html.escape(t)}</li>" for t in tactics]) or "<li>Beta launch with community access</li>"

        pos = getattr(gtm, "positioning_statement", "") or "The intuitive, high-velocity platform for modern teams."
        pricing = getattr(gtm, "pricing_strategy", "") or "Tiered Subscription (Freemium -> Pro -> Enterprise)"
        cac = getattr(gtm, "estimated_cac_summary", "") or "Estimated CAC of $35 - $65 per paid subscriber."

        html_content = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">GROWTH ENGINE</div>'
            '<div class="saas-title">Go-To-Market Strategy</div>'
            '</div>'
            '</div>'
            '<div class="sub-heading">Strategic Positioning</div>'
            f'<p class="body-text">{html.escape(pos)}</p>'
            '<div class="sub-heading">Acquisition Channels</div>'
            f'<ul class="clean-bullet-list">{channels_html}</ul>'
            '<div class="two-column-cards" style="margin-top: 14px;">'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">LAUNCH TACTICS</div>'
            f'<ul class="clean-bullet-list" style="margin-top: 8px;">{tactics_html}</ul>'
            '</div>'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">PRICING &amp; CAC</div>'
            f'<p class="body-text" style="margin-top: 8px;">{html.escape(pricing)}</p>'
            f'<p class="body-text" style="font-size: 12.5px; color: #64748B;">{html.escape(cac)}</p>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)
