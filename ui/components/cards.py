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
    ValidationReport,
)


def _get_score_status(score: int) -> tuple[str, str]:
    """Returns status text and CSS class based on overall viability score."""
    if score >= 78:
        return "Strong", "status-strong"
    elif score >= 65:
        return "Moderate", "status-moderate"
    elif score >= 50:
        return "Pivot", "status-moderate"
    else:
        return "Caution", "status-caution"


def _generate_score_ring_html(score: int) -> str:
    """Generates a clean, robust CSS conic-gradient circular score ring."""
    stroke_color = "#22C55E" if score >= 78 else ("#F59E0B" if score >= 50 else "#EF4444")
    deg = int((score / 100.0) * 360)
    return (
        f'<div class="circular-score-wrapper" style="width: 96px; height: 96px; border-radius: 50%; '
        f'background: conic-gradient({stroke_color} {deg}deg, #F1F5F9 {deg}deg 360deg); '
        f'display: flex; align-items: center; justify-content: center; margin: 0.5rem auto;">'
        f'<div style="width: 78px; height: 78px; border-radius: 50%; background: #FFFFFF; '
        f'display: flex; flex-direction: column; align-items: center; justify-content: center;">'
        f'<span class="score-num" style="font-size: 1.7rem; font-weight: 800; color: #0F172A; line-height: 1;">{score}</span>'
        f'<span class="score-denom" style="font-size: 0.72rem; font-weight: 600; color: #64748B;">/ 100</span>'
        f'</div>'
        f'</div>'
    )


def _is_safe_url(url: str) -> bool:
    """Validates whether a URL is a safe external HTTP or HTTPS link."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


class CardComponents:
    """Clean, Modern SaaS HTML Card Components for Startup Validation Dashboard & Report."""

    @staticmethod
    def render_kpi_metrics_row(state: Optional[StartupState] = None) -> None:
        """Renders the top KPI metrics row using actual values from the report model."""
        if state and state.final_report:
            report = state.final_report
            market = state.market_analysis
            comp = state.competitor_analysis

            score_val = f"{report.overall_viability_score}"
            score_sub = f"Verdict: {report.verdict}"

            market_val = f"{report.market_score}"
            tam_val = getattr(market, "tam_billions", None) if market else None
            tam_str = f"TAM ${tam_val:.1f}B" if tam_val is not None else "Market Sizing"

            comp_val = f"{report.competitor_score}"
            direct_comps = getattr(comp, "direct_competitors", []) if comp else []
            comp_sub = f"{len(direct_comps)} Incumbents" if direct_comps else "Competitive Moat"

            mvp_val = f"{report.mvp_score}"
            mvp_sub = "Readiness High" if report.mvp_score >= 70 else "Readiness Moderate"

            risk_resilience = max(0, min(100, int((10.0 - report.risk_score) * 10)))
            risk_val = f"{risk_resilience}"
            risk_sub = f"Risk Index {report.risk_score}/10"

            gtm_val = f"{report.gtm_score}"
            gtm_sub = f"Funding {report.funding_probability}%" if getattr(report, "funding_probability", None) is not None else "GTM Execution"
        else:
            score_val = "--"
            score_sub = "Awaiting Idea"
            market_val = "--"
            tam_str = "Market Sizing"
            comp_val = "--"
            comp_sub = "Competitive Moat"
            mvp_val = "--"
            mvp_sub = "Readiness"
            risk_val = "--"
            risk_sub = "Risk Resilience"
            gtm_val = "--"
            gtm_sub = "Go-To-Market"

        html_content = (
            '<div class="kpi-score-cards-grid">'
            '<div class="kpi-mini-card kpi-hero">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">Viability Score</span>'
            '</div>'
            f'<div class="kpi-val-hero">{score_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{html.escape(score_sub)}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-market">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">Market Score</span>'
            '</div>'
            f'<div class="kpi-val-hero">{market_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{html.escape(tam_str)}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-comp">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">Competition</span>'
            '</div>'
            f'<div class="kpi-val-hero">{comp_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{html.escape(comp_sub)}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-mvp">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">MVP Readiness</span>'
            '</div>'
            f'<div class="kpi-val-hero">{mvp_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{html.escape(mvp_sub)}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-risk">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">Risk Resilience</span>'
            '</div>'
            f'<div class="kpi-val-hero">{risk_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{html.escape(risk_sub)}</div>'
            '</div>'
            '<div class="kpi-mini-card kpi-gtm">'
            '<div class="kpi-label-row">'
            '<span class="kpi-card-label">GTM Execution</span>'
            '</div>'
            f'<div class="kpi-val-hero">{gtm_val}<span style="font-size: 14px; font-weight: 600; color: #64748B;">/100</span></div>'
            f'<div class="kpi-val-sub">{html.escape(gtm_sub)}</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_dimension_progress_breakdown(state: StartupState) -> None:
        """Renders the actual score dimensions from ScoringBreakdown or ValidationReport."""
        if not state or not state.final_report:
            return

        report = state.final_report
        scoring = report.scoring_breakdown

        rows = []
        if scoring:
            # Render real fields from ScoringBreakdown
            dimension_data = [
                ("Market Opportunity", scoring.market_opportunity_score, 20, "fill-blue"),
                ("Innovation & Differentiation", scoring.innovation_score, 15, "fill-green"),
                ("Competition & Moat", scoring.competition_score, 15, "fill-indigo"),
                ("Scalability Potential", scoring.scalability_score, 15, "fill-purple"),
                ("Technical Feasibility", scoring.technical_feasibility_score, 10, "fill-blue"),
                ("Revenue Model Viability", scoring.revenue_model_score, 10, "fill-green"),
                ("Execution & Risk Resilience", scoring.execution_risk_score, 10, "fill-orange"),
                ("Market Timing", scoring.market_timing_score, 5, "fill-purple"),
            ]
            for label, score, max_val, fill_cls in dimension_data:
                pct = int((score / max_val) * 100) if max_val > 0 else 0
                rows.append(
                    f'<div class="dim-bar-row">'
                    f'<div class="dim-bar-header">'
                    f'<span class="dim-bar-title">{html.escape(label)}</span>'
                    f'<span class="dim-bar-val">{score} / {max_val} ({pct}%)</span>'
                    f'</div>'
                    f'<div class="dim-progress-track">'
                    f'<div class="dim-progress-fill {fill_cls}" style="width: {pct}%;"></div>'
                    f'</div>'
                    f'</div>'
                )
        else:
            # Fallback to dimensions directly present on ValidationReport
            risk_resilience = max(0, min(100, int((10.0 - report.risk_score) * 10)))
            dimension_data = [
                ("Market Opportunity", report.market_score, 100, "fill-blue"),
                ("Competitive Defensibility", report.competitor_score, 100, "fill-indigo"),
                ("MVP Readiness", report.mvp_score, 100, "fill-green"),
                ("Risk Resilience", risk_resilience, 100, "fill-orange"),
                ("Go-To-Market Strategy", report.gtm_score, 100, "fill-purple"),
            ]
            for label, score, max_val, fill_cls in dimension_data:
                rows.append(
                    f'<div class="dim-bar-row">'
                    f'<div class="dim-bar-header">'
                    f'<span class="dim-bar-title">{html.escape(label)}</span>'
                    f'<span class="dim-bar-val">{score} / {max_val}</span>'
                    f'</div>'
                    f'<div class="dim-progress-track">'
                    f'<div class="dim-progress-fill {fill_cls}" style="width: {score}%;"></div>'
                    f'</div>'
                    f'</div>'
                )

        dim_list_html = "".join(rows)

        html_content = (
            '<div class="saas-card dimension-bars-card">'
            '<div class="saas-card-header" style="margin-bottom: 1rem;">'
            '<div>'
            '<div class="saas-card-label">STRATEGIC WEIGHTED METRICS</div>'
            '<div class="saas-title" style="font-size: 1.15rem;">Deterministic Score Matrix Breakdown</div>'
            '</div>'
            '</div>'
            f'<div class="dimension-bars-list">{dim_list_html}</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_score_overview_section(state: StartupState) -> None:
        """Renders the top 3-card score overview (Ring, Core Dimensions, Strategic Verdict)."""
        if not state or not state.final_report:
            return

        report = state.final_report
        status_text, status_cls = _get_score_status(report.overall_viability_score)
        ring_html = _generate_score_ring_html(int(report.overall_viability_score))
        verdict_val = report.verdict.upper()

        market_pct = report.market_score
        comp_pct = report.competitor_score
        risk_pct = max(0, min(100, int((10.0 - report.risk_score) * 10)))
        mvp_pct = report.mvp_score

        # Select summary explanation from actual report data
        if report.key_takeaways:
            insight_text = report.key_takeaways[0]
        else:
            insight_text = report.executive_summary[:240] + "..." if len(report.executive_summary) > 240 else report.executive_summary

        html_content = (
            '<div class="score-overview-grid">'
            '<div class="saas-card circular-score-card">'
            '<div class="saas-card-label">STARTUP VIABILITY SCORE</div>'
            f'{ring_html}'
            f'<div class="score-verdict-badge {status_cls}">{html.escape(verdict_val)}</div>'
            '</div>'
            '<div class="saas-card dimension-bars-card">'
            '<div class="saas-card-label">CORE BENCHMARK METRICS</div>'
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
            '<span class="dim-bar-title">Competition &amp; Moat</span>'
            f'<span class="dim-bar-val">{comp_pct}%</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-indigo" style="width: {comp_pct}%;"></div>'
            '</div>'
            '</div>'
            '<div class="dim-bar-row">'
            '<div class="dim-bar-header">'
            '<span class="dim-bar-title">MVP Feasibility</span>'
            f'<span class="dim-bar-val">{mvp_pct}%</span>'
            '</div>'
            '<div class="dim-progress-track">'
            f'<div class="dim-progress-fill fill-green" style="width: {mvp_pct}%;"></div>'
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
            f'<div class="insight-heading">Verdict: {html.escape(verdict_val)}</div>'
            f'<div class="insight-body">{html.escape(insight_text)}</div>'
            '</div>'
            f'<div class="verdict-pill verdict-{verdict_val.lower()}">{html.escape(verdict_val)}</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_executive_summary_tab(state: StartupState) -> None:
        """Renders the clean Executive Summary tab from actual report data."""
        if not state or not state.final_report:
            return

        report = state.final_report
        swot = state.swot_analysis
        market = state.market_analysis
        comp = state.competitor_analysis

        strengths = getattr(swot, "strengths", []) if swot else getattr(report, "key_takeaways", [])
        threats = getattr(swot, "threats", []) if swot else []

        strengths_items = "".join([f"<li>{html.escape(s)}</li>" for s in strengths[:4]]) if strengths else "<li style='color: #94A3B8; font-style: italic;'>No specific strengths highlighted in analysis.</li>"
        threats_items = "".join([f"<li>{html.escape(t)}</li>" for t in threats[:4]]) if threats else "<li style='color: #94A3B8; font-style: italic;'>No critical threats highlighted in analysis.</li>"

        next_steps = getattr(report, "recommended_next_steps", [])
        next_steps_items = "".join([f"<li>{html.escape(step)}</li>" for step in next_steps]) if next_steps else "<li style='color: #94A3B8; font-style: italic;'>No recommended next steps provided.</li>"

        tam_val = getattr(market, "tam_billions", None) if market else None
        tam_display = f"${tam_val:.1f}B" if tam_val is not None else "Not available"

        direct_comps = getattr(comp, "direct_competitors", []) if comp else []
        comp_count_str = str(len(direct_comps)) if direct_comps else "0 identified"

        mvp_score_str = str(report.mvp_score) if getattr(report, "mvp_score", None) is not None else "Not available"
        funding_prob_str = f"{report.funding_probability}%" if getattr(report, "funding_probability", None) is not None else "Not available"

        html_content = (
            '<div class="tab-content-container">'
            '<div class="saas-card">'
            '<div class="saas-card-label">EXECUTIVE SYNTHESIS</div>'
            '<div class="saas-title" style="font-size: 1.15rem; margin-bottom: 8px;">Executive Summary</div>'
            f'<p class="body-text">{html.escape(report.executive_summary)}</p>'
            '</div>'
            '<div class="two-column-cards">'
            '<div class="saas-card strengths-card">'
            '<span class="card-pill pill-green">KEY OPPORTUNITIES &amp; STRENGTHS</span>'
            f'<ul class="clean-bullet-list">{strengths_items}</ul>'
            '</div>'
            '<div class="saas-card risks-card">'
            '<span class="card-pill pill-red">KEY CONCERNS &amp; THREATS</span>'
            f'<ul class="clean-bullet-list">{threats_items}</ul>'
            '</div>'
            '</div>'
            '<div class="saas-card">'
            '<div class="saas-card-label">ACTIONABLE ROADMAP</div>'
            '<div class="saas-title" style="font-size: 1.05rem; margin-bottom: 8px;">Recommended Next Steps</div>'
            f'<ul class="clean-bullet-list">{next_steps_items}</ul>'
            '</div>'
            '<div class="lower-metrics-grid">'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Market Opportunity</div>'
            f'<div class="metric-hero-val">{html.escape(tam_display)}</div>'
            '<div class="metric-caption">Estimated TAM</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Competition</div>'
            f'<div class="metric-hero-val">{html.escape(comp_count_str)}</div>'
            '<div class="metric-caption">Direct Competitors</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">MVP Readiness</div>'
            f'<div class="metric-hero-val">{html.escape(mvp_score_str)}</div>'
            '<div class="metric-caption">Feasibility Score</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Funding Potential</div>'
            f'<div class="metric-hero-val">{html.escape(funding_prob_str)}</div>'
            '<div class="metric-caption">Investor Probability</div>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_market_card(market: Any) -> None:
        """Renders the Market Analysis tab card strictly using real report data."""
        tam = getattr(market, "tam_billions", None)
        sam = getattr(market, "sam_billions", None)
        som = getattr(market, "som_billions", None)
        cagr = getattr(market, "cagr_percentage", None)
        overview = getattr(market, "market_size_summary", "") or ""
        drivers = getattr(market, "key_growth_drivers", []) or []
        personas = getattr(market, "target_personas", []) or []

        tam_str = f"${tam:.1f}B" if tam is not None else "Not available"
        sam_str = f"${sam:.1f}B" if sam is not None else "Not available"
        som_str = f"${som:.2f}B" if som is not None else "Not available"
        cagr_str = f"{cagr:.1f}%" if cagr is not None else "Not available"

        growth_html = "".join([f"<li>{html.escape(g)}</li>" for g in drivers]) if drivers else "<li style='color: #94A3B8; font-style: italic;'>No growth drivers identified.</li>"

        personas_html = ""
        for p in personas:
            if hasattr(p, "role"):
                p_role = html.escape(p.role)
                p_wtp = html.escape(str(getattr(p, "willingness_to_pay", "Medium")))
                pains = getattr(p, "pain_points", [])
                p_pains = ", ".join([html.escape(pn) for pn in pains]) if pains else "Not specified"
                personas_html += f"<li><strong>{p_role}</strong> (WTP: {p_wtp}) &bull; Pain points: {p_pains}</li>"
            else:
                personas_html += f"<li>{html.escape(str(p))}</li>"

        if not personas_html:
            personas_html = "<li style='color: #94A3B8; font-style: italic;'>No target personas recorded in analysis.</li>"

        overview_html = f'<p class="body-text">{html.escape(overview)}</p>' if overview else ""

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
            f'<div class="metric-hero-val">{html.escape(tam_str)}</div>'
            '<div class="metric-caption">TAM Sizing</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Serviceable Addressable</div>'
            f'<div class="metric-hero-val">{html.escape(sam_str)}</div>'
            '<div class="metric-caption">SAM Sizing</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Serviceable Obtainable</div>'
            f'<div class="metric-hero-val">{html.escape(som_str)}</div>'
            '<div class="metric-caption">SOM Sizing</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Compound Annual Growth</div>'
            f'<div class="metric-hero-val">{html.escape(cagr_str)}</div>'
            '<div class="metric-caption">Projected CAGR</div>'
            '</div>'
            '</div>'
            f'{overview_html}'
            '<div class="two-column-cards" style="margin-top: 14px;">'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">GROWTH DRIVERS</div>'
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
        """Renders the Competitor Comparison UI with distinct direct vs indirect cards and real data only."""
        direct = getattr(comp, "direct_competitors", []) or []
        indirect = getattr(comp, "indirect_competitors", []) or []
        moat = getattr(comp, "moat_assessment", "") or ""
        pos_summary = getattr(comp, "market_positioning_summary", "") or ""

        cards_html = []

        def _render_comp_item(c, comp_type_label: str):
            name = getattr(c, "name", "Competitor")
            url = getattr(c, "url", "")
            desc = getattr(c, "description", "")
            pricing = getattr(c, "pricing_model", "")
            strengths = getattr(c, "strengths", []) or []
            weaknesses = getattr(c, "weaknesses", []) or []
            features = getattr(c, "key_features", []) or []

            link_html = ""
            if _is_safe_url(url):
                link_html = (
                    f' &bull; <a href="{html.escape(url.strip(), quote=True)}" '
                    f'target="_blank" rel="noopener noreferrer" '
                    f'style="color: #2563EB; font-size: 12px; text-decoration: none; font-weight: 600;">'
                    f'Website &rarr;</a>'
                )

            str_items = "".join([f"<li>{html.escape(s)}</li>" for s in strengths]) if strengths else "<li style='color: #94A3B8; font-style: italic;'>Not available</li>"
            weak_items = "".join([f"<li>{html.escape(w)}</li>" for w in weaknesses]) if weaknesses else "<li style='color: #94A3B8; font-style: italic;'>Not available</li>"
            feat_pills = "".join([f'<span class="competitor-feature-tag">{html.escape(f)}</span>' for f in features]) if features else ""

            desc_html = f'<div class="competitor-desc">{html.escape(desc)}</div>' if desc else ""
            pricing_html = f'<div class="competitor-pricing-tag">Pricing: <strong>{html.escape(pricing)}</strong></div>' if pricing else ""
            features_html = f'<div class="competitor-features-row">{feat_pills}</div>' if feat_pills else ""

            type_badge = f'<span class="source-domain-pill" style="margin-left: 8px;">{html.escape(comp_type_label)}</span>'

            return (
                '<div class="competitor-item-card">'
                '<div class="competitor-card-header">'
                '<div>'
                f'<span class="competitor-name">{html.escape(name)}</span>{type_badge}{link_html}'
                f'{desc_html}'
                '</div>'
                '</div>'
                f'{pricing_html}'
                f'{features_html}'
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

        for c in direct:
            cards_html.append(_render_comp_item(c, "Direct Incumbent"))

        for c in indirect:
            cards_html.append(_render_comp_item(c, "Indirect / Alternative"))

        competitors_grid = "".join(cards_html) if cards_html else "<p class='body-text' style='color: #64748B;'>No competitor records identified in analysis.</p>"

        pos_html = f'<div class="saas-card" style="margin-bottom: 0;"><div class="saas-card-label">MARKET POSITIONING</div><p class="body-text" style="margin-top: 6px;">{html.escape(pos_summary)}</p></div>' if pos_summary else ""
        moat_html = f'<div class="saas-card" style="margin-bottom: 0;"><div class="saas-card-label">DEFENSIBLE MOAT ASSESSMENT</div><p class="body-text" style="margin-top: 6px;">{html.escape(moat)}</p></div>' if moat else ""

        top_row_html = f'<div class="two-column-cards" style="margin-bottom: 16px;">{pos_html}{moat_html}</div>' if (pos_html or moat_html) else ""

        html_content = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">COMPETITIVE DUE DILIGENCE</div>'
            '<div class="saas-title">Competitor Comparison &amp; Defensibility</div>'
            '</div>'
            '</div>'
            f'{top_row_html}'
            f'<div class="competitor-cards-container">{competitors_grid}</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    render_competitor_card = render_competitors_card

    @staticmethod
    def render_risk_section(swot: Any) -> None:
        """Renders the structured Risk Analysis section using real risk_matrix data."""
        risk_matrix = getattr(swot, "risk_matrix", []) or []
        fin_risk = getattr(swot, "financial_risk", None)
        tech_risk = getattr(swot, "technical_risk", None)
        reg_risk = getattr(swot, "regulatory_risk", None)
        overall_risk = getattr(swot, "overall_risk_score", None)
        mitigation_plan = getattr(swot, "risk_mitigation_plan", []) or []

        risk_cards = []
        for r in risk_matrix:
            r_name = getattr(r, "risk_name", "Venture Risk")
            cat = getattr(r, "category", "Execution")
            prob = getattr(r, "probability", None)
            imp = getattr(r, "impact", None)
            sev = getattr(r, "severity_score", (prob * imp if prob and imp else None))
            mit = getattr(r, "mitigation_strategy", "")

            # Determine severity label and class
            if sev is not None:
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
                sev_str = f"{sev}/25"
            else:
                sev_label = "Assessed"
                sev_cls = "sev-moderate"
                sev_str = "--"

            prob_str = f"Probability: {prob}/5" if prob is not None else ""
            imp_str = f"Impact: {imp}/5" if imp is not None else ""
            metric_sub = " &bull; ".join(filter(None, [prob_str, imp_str]))

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
                f'<span class="risk-severity-pill {sev_cls}">{sev_label} &bull; {sev_str}</span>'
                '</div>'
                f'<div class="risk-metric-subtext">{metric_sub}</div>'
                f'{mit_html}'
                '</div>'
            )

        risks_html = "".join(risk_cards) if risk_cards else "<p class='body-text' style='color: #64748B;'>No quantified risk items found in analysis.</p>"

        plan_items = "".join([f"<li>{html.escape(p)}</li>" for p in mitigation_plan]) if mitigation_plan else "<li style='color: #94A3B8; font-style: italic;'>No specific risk mitigation roadmap items recorded.</li>"

        overall_str = f"{overall_risk}/10" if overall_risk is not None else "Not available"
        fin_str = f"{fin_risk}/10" if fin_risk is not None else "Not available"
        tech_str = f"{tech_risk}/10" if tech_risk is not None else "Not available"
        reg_str = f"{reg_risk}/10" if reg_risk is not None else "Not available"

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
            f'<div class="metric-hero-val">{html.escape(overall_str)}</div>'
            '<div class="metric-caption">Aggregate Risk</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Financial Risk</div>'
            f'<div class="metric-hero-val">{html.escape(fin_str)}</div>'
            '<div class="metric-caption">Capital Exposure</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Technical Risk</div>'
            f'<div class="metric-hero-val">{html.escape(tech_str)}</div>'
            '<div class="metric-caption">Complexity Risk</div>'
            '</div>'
            '<div class="lower-metric-card">'
            '<div class="metric-category">Regulatory Risk</div>'
            f'<div class="metric-hero-val">{html.escape(reg_str)}</div>'
            '<div class="metric-caption">Compliance Exposure</div>'
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

                link_action = ""
                if _is_safe_url(url):
                    link_action = (
                        f'<a href="{html.escape(url.strip(), quote=True)}" '
                        f'target="_blank" rel="noopener noreferrer" '
                        f'class="source-card-action">'
                        f'Open Source &rarr;'
                        f'</a>'
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
            f'<div class="saas-card-subtext">Real-time market insights and external validation research gathered via Tavily Search API ({total_sources} research sources).</div>'
            '</div>'
            '</div>'
            f'{grid_html}'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_mvp_card(mvp: Any) -> None:
        """Renders the MVP Recommendation tab card strictly using actual report data."""
        features = getattr(mvp, "features", []) or []
        features_html = ""
        for f in features:
            if hasattr(f, "feature_name"):
                prio = html.escape(str(getattr(f, "priority", "Must Have")))
                desc = f": {html.escape(f.description)}" if getattr(f, "description", "") else ""
                features_html += f"<li><strong>{html.escape(f.feature_name)}</strong> ({prio}){desc}</li>"
            else:
                features_html += f"<li>{html.escape(str(f))}</li>"
        if not features_html:
            features_html = "<li style='color: #94A3B8; font-style: italic;'>No prioritized MVP features identified.</li>"

        fe = html.escape(str(getattr(mvp, "tech_stack_frontend", "Streamlit / Modern CSS")))
        be = html.escape(str(getattr(mvp, "tech_stack_backend", "Python / LangGraph")))
        db = html.escape(str(getattr(mvp, "tech_stack_database", "PostgreSQL / SQLite")))
        ai = html.escape(str(getattr(mvp, "tech_stack_ai", "Google Gemini & Tavily")))

        # 4-Week Roadmap: only render if actual roadmap exists in the data
        roadmap = getattr(mvp, "four_week_roadmap", {}) or {}
        if roadmap and isinstance(roadmap, dict):
            roadmap_items = "".join([f"<li><strong>{html.escape(str(w))}:</strong> {html.escape(str(t))}</li>" for w, t in roadmap.items()])
            roadmap_html = (
                '<div class="saas-card" style="margin-bottom: 0;">'
                '<div class="saas-card-label">BUILD ROADMAP</div>'
                f'<ul class="clean-bullet-list" style="margin-top: 8px;">{roadmap_items}</ul>'
                '</div>'
            )
        else:
            roadmap_html = ""

        # Key Metrics / KPIs
        kpis = getattr(mvp, "key_metrics_kpis", []) or []
        if kpis:
            kpi_items = "".join([f"<li>{html.escape(str(k))}</li>" for k in kpis])
            kpis_card_html = (
                '<div class="saas-card" style="margin-bottom: 0;">'
                '<div class="saas-card-label">VALIDATION KPIS &amp; METRICS</div>'
                f'<ul class="clean-bullet-list" style="margin-top: 8px;">{kpi_items}</ul>'
                '</div>'
            )
        else:
            kpis_card_html = ""

        second_card_html = roadmap_html or kpis_card_html or (
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">VALIDATION APPROACH</div>'
            '<p class="body-text" style="margin-top: 8px; color: #64748B;">Iterative user feedback validation recommended for initial release.</p>'
            '</div>'
        )

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
            f'{second_card_html}'
            '</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_swot_risk_card(swot: Any) -> None:
        """Renders the 4-quadrant SWOT Matrix tab card strictly using real report data."""
        str_list = getattr(swot, "strengths", []) or []
        weak_list = getattr(swot, "weaknesses", []) or []
        opp_list = getattr(swot, "opportunities", []) or []
        thr_list = getattr(swot, "threats", []) or []

        str_html = "".join([f"<li>{html.escape(s)}</li>" for s in str_list]) if str_list else "<li style='color: #94A3B8; font-style: italic;'>None identified in analysis.</li>"
        weak_html = "".join([f"<li>{html.escape(w)}</li>" for w in weak_list]) if weak_list else "<li style='color: #94A3B8; font-style: italic;'>None identified in analysis.</li>"
        opp_html = "".join([f"<li>{html.escape(o)}</li>" for o in opp_list]) if opp_list else "<li style='color: #94A3B8; font-style: italic;'>None identified in analysis.</li>"
        thr_html = "".join([f"<li>{html.escape(t)}</li>" for t in thr_list]) if thr_list else "<li style='color: #94A3B8; font-style: italic;'>None identified in analysis.</li>"

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

    render_swot_card = render_swot_risk_card

    @staticmethod
    def render_gtm_card(gtm: Any) -> None:
        """Renders the Go-To-Market Strategy tab card strictly using real report data."""
        channels = getattr(gtm, "primary_acquisition_channels", []) or []
        channels_html = ""
        for c in channels:
            if hasattr(c, "channel_name"):
                desc = f": {html.escape(c.description)}" if getattr(c, "description", "") else ""
                channels_html += f"<li><strong>{html.escape(c.channel_name)}</strong>{desc}</li>"
            else:
                channels_html += f"<li><strong>{html.escape(str(c))}</strong></li>"
        if not channels_html:
            channels_html = "<li style='color: #94A3B8; font-style: italic;'>No acquisition channels specified.</li>"

        tactics = getattr(gtm, "launch_tactics", []) or []
        tactics_html = "".join([f"<li>{html.escape(t)}</li>" for t in tactics]) if tactics else "<li style='color: #94A3B8; font-style: italic;'>No specific launch tactics specified.</li>"

        pos = getattr(gtm, "positioning_statement", "") or ""
        pricing = getattr(gtm, "pricing_strategy", "") or ""
        cac = getattr(gtm, "estimated_cac_summary", "") or ""

        pos_html = f'<div class="sub-heading">Strategic Positioning</div><p class="body-text">{html.escape(pos)}</p>' if pos else ""
        pricing_html = f'<p class="body-text" style="margin-top: 8px;">{html.escape(pricing)}</p>' if pricing else "<p class='body-text' style='color: #94A3B8; font-style: italic;'>Pricing strategy not specified.</p>"
        cac_html = f'<p class="body-text" style="font-size: 12.5px; color: #64748B;">{html.escape(cac)}</p>' if cac else ""

        html_content = (
            '<div class="saas-card">'
            '<div class="saas-card-header">'
            '<div>'
            '<div class="saas-card-label">GROWTH ENGINE</div>'
            '<div class="saas-title">Go-To-Market Strategy</div>'
            '</div>'
            '</div>'
            f'{pos_html}'
            '<div class="sub-heading">Acquisition Channels</div>'
            f'<ul class="clean-bullet-list">{channels_html}</ul>'
            '<div class="two-column-cards" style="margin-top: 14px;">'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">LAUNCH TACTICS</div>'
            f'<ul class="clean-bullet-list" style="margin-top: 8px;">{tactics_html}</ul>'
            '</div>'
            '<div class="saas-card" style="margin-bottom: 0;">'
            '<div class="saas-card-label">PRICING &amp; CAC</div>'
            f'{pricing_html}'
            f'{cac_html}'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)
