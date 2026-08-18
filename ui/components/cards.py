import streamlit as st
from typing import Optional, List
from state.schema import (
    StartupState,
    ValidationReport,
    MarketAnalysis,
    CompetitorAnalysis,
    SWOTAnalysis,
    MVPRecommendation,
    GTMStrategy,
)


def _get_score_status(score: float, is_risk: bool = False) -> tuple[str, str]:
    """Returns status label and CSS class for a given score value."""
    if is_risk:
        if score <= 3.5:
            return "Low Risk", "status-strong"
        elif score <= 6.5:
            return "Moderate Risk", "status-moderate"
        else:
            return "High Risk", "status-caution"
    else:
        if score >= 75:
            return "Strong", "status-strong"
        elif score >= 50:
            return "Moderate", "status-moderate"
        else:
            return "Needs Work", "status-caution"


def _generate_score_ring_svg(score: int) -> str:
    """Generates an SVG circular progress ring for the overall viability score."""
    # Circumference for r=38 is ~238.76
    radius = 38
    circumference = 2 * 3.14159 * radius
    stroke_dashoffset = circumference - (score / 100.0) * circumference
    
    stroke_color = "#22C55E" if score >= 75 else ("#F59E0B" if score >= 50 else "#EF4444")
    
    return f"""
    <svg class="score-ring-svg" viewBox="0 0 96 96" width="96" height="96">
      <circle cx="48" cy="48" r="{radius}" class="score-ring-bg" stroke="#E2E8F0" stroke-width="8" fill="none"/>
      <circle cx="48" cy="48" r="{radius}" class="score-ring-progress" stroke="{stroke_color}" stroke-width="8" stroke-linecap="round" fill="none"
              stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{stroke_dashoffset:.2f}"
              transform="rotate(-90 48 48)"/>
      <text x="48" y="46" class="score-ring-text-val" text-anchor="middle" dominant-baseline="central">{score}</text>
      <text x="48" y="62" class="score-ring-text-unit" text-anchor="middle" dominant-baseline="central">/100</text>
    </svg>
    """


class CardComponents:
    """Clean, Modern SaaS HTML Card Components for Startup Validation Report."""

    @staticmethod
    def render_score_overview_section(state: StartupState) -> None:
        """Renders the top 3-card overview: Validation Score Ring, Dimension Progress Bars, and Key Insight."""
        report = state.final_report
        if not report:
            return

        status_text, status_cls = _get_score_status(report.overall_viability_score)
        ring_svg = _generate_score_ring_svg(int(report.overall_viability_score))

        # Risk score normalized to 100 scale for progress bar display
        risk_pct = min(100, int(report.risk_score * 10))
        risk_label_val = f"{report.risk_score}/10"

        # Insight text
        insight_text = report.key_takeaways[0] if report.key_takeaways else report.executive_summary[:200] + "..."

        st.markdown(f"""
<div class="score-overview-grid">
  
  <!-- 1. Circular Validation Score Card -->
  <div class="saas-card score-hero-card">
    <div class="saas-card-label">VALIDATION SCORE</div>
    <div class="score-ring-container">
      {ring_svg}
    </div>
    <div class="score-verdict-badge {status_cls}">{status_text}</div>
  </div>

  <!-- 2. Dimension Scores Progress Bars Card -->
  <div class="saas-card dimension-bars-card">
    <div class="saas-card-label">DIMENSION SCORES</div>
    <div class="dimension-bars-list">
      
      <div class="dim-bar-row">
        <div class="dim-bar-header">
          <span class="dim-bar-title">Market</span>
          <span class="dim-bar-val">{report.market_score}</span>
        </div>
        <div class="dim-progress-track">
          <div class="dim-progress-fill fill-blue" style="width: {report.market_score}%;"></div>
        </div>
      </div>

      <div class="dim-bar-row">
        <div class="dim-bar-header">
          <span class="dim-bar-title">Competition</span>
          <span class="dim-bar-val">{report.competitor_score}</span>
        </div>
        <div class="dim-progress-track">
          <div class="dim-progress-fill fill-blue" style="width: {report.competitor_score}%;"></div>
        </div>
      </div>

      <div class="dim-bar-row">
        <div class="dim-bar-header">
          <span class="dim-bar-title">MVP</span>
          <span class="dim-bar-val">{report.mvp_score}</span>
        </div>
        <div class="dim-progress-track">
          <div class="dim-progress-fill fill-green" style="width: {report.mvp_score}%;"></div>
        </div>
      </div>

      <div class="dim-bar-row">
        <div class="dim-bar-header">
          <span class="dim-bar-title">Risk Resilience</span>
          <span class="dim-bar-val">{100 - risk_pct}</span>
        </div>
        <div class="dim-progress-track">
          <div class="dim-progress-fill fill-orange" style="width: {100 - risk_pct}%;"></div>
        </div>
      </div>

      <div class="dim-bar-row">
        <div class="dim-bar-header">
          <span class="dim-bar-title">GTM</span>
          <span class="dim-bar-val">{report.gtm_score}</span>
        </div>
        <div class="dim-progress-track">
          <div class="dim-progress-fill fill-purple" style="width: {report.gtm_score}%;"></div>
        </div>
      </div>

    </div>
  </div>

  <!-- 3. Key Insight Card -->
  <div class="saas-card key-insight-card">
    <div class="saas-card-label">KEY INSIGHT</div>
    <div class="insight-heading">Strategic Recommendation</div>
    <p class="insight-body">{insight_text}</p>
    <div class="verdict-pill verdict-{report.verdict.lower().replace(' ', '-')}">Verdict: {report.verdict}</div>
  </div>

</div>
""", unsafe_allow_html=True)

    @staticmethod
    def render_executive_summary_tab(state: StartupState) -> None:
        """Renders the executive summary tab with Overall Assessment, Strengths, Risks, and 4 Metric Cards."""
        report = state.final_report
        swot = state.swot_analysis
        market = state.market_analysis
        comp = state.competitor_analysis
        if not report:
            return

        strengths_list = swot.strengths if swot and swot.strengths else report.key_takeaways[:3]
        risks_list = swot.threats if swot and swot.threats else [f"Market Risk: Severity {report.risk_score}/10"]
        
        strengths_html = "".join([f"<li>{s}</li>" for s in strengths_list])
        risks_html = "".join([f"<li>{r}</li>" for r in risks_list])

        tam_str = f"${market.tam_billions}B" if market else "N/A"
        comp_count = f"{len(comp.direct_competitors)}" if comp and comp.direct_competitors else "0"

        st.markdown(f"""
<div class="tab-content-container">

  <!-- Overall Assessment -->
  <div class="saas-card">
    <div class="saas-card-label">OVERALL ASSESSMENT</div>
    <div class="saas-title">Executive Summary</div>
    <p class="body-text">{report.executive_summary}</p>
  </div>

  <!-- Two Supporting Cards: Key Strengths & Main Risks -->
  <div class="two-column-cards">
    <div class="saas-card strengths-card">
      <div class="card-pill pill-green">KEY STRENGTHS</div>
      <ul class="clean-bullet-list">
        {strengths_html}
      </ul>
    </div>
    <div class="saas-card risks-card">
      <div class="card-pill pill-red">MAIN RISKS</div>
      <ul class="clean-bullet-list">
        {risks_html}
      </ul>
    </div>
  </div>

  <!-- Lower Metric Cards Grid -->
  <div class="lower-metrics-grid">
    <div class="lower-metric-card">
      <div class="metric-category">Market Opportunity</div>
      <div class="metric-hero-val">{tam_str}</div>
      <div class="metric-caption">TAM Market Size</div>
    </div>
    <div class="lower-metric-card">
      <div class="metric-category">Competition</div>
      <div class="metric-hero-val">{comp_count}</div>
      <div class="metric-caption">Key Incumbents Identified</div>
    </div>
    <div class="lower-metric-card">
      <div class="metric-category">MVP Readiness</div>
      <div class="metric-hero-val">{report.mvp_score}/100</div>
      <div class="metric-caption">Technical Feasibility</div>
    </div>
    <div class="lower-metric-card">
      <div class="metric-category">Funding Potential</div>
      <div class="metric-hero-val">{report.funding_probability}%</div>
      <div class="metric-caption">Investor Readiness {report.investor_readiness_score}/100</div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

    @staticmethod
    def render_market_card(market: MarketAnalysis) -> None:
        if not market:
            return

        drivers_html = "".join([f"<li>{d}</li>" for d in market.key_growth_drivers])
        readiness_status, readiness_cls = _get_score_status(market.market_readiness_score)

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div>
      <div class="saas-card-label">MARKET ANALYSIS</div>
      <div class="saas-title">Market Opportunity & Sizing</div>
    </div>
    <span class="metric-tag">Readiness: {market.market_readiness_score}/100 ({readiness_status})</span>
  </div>

  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-value">${market.tam_billions}B</div>
      <div class="metric-label">TAM (Total Addressable)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${market.sam_billions}B</div>
      <div class="metric-label">SAM (Serviceable)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${market.som_billions}B</div>
      <div class="metric-label">SOM (Obtainable)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{market.cagr_percentage}%</div>
      <div class="metric-label">Annual CAGR</div>
    </div>
  </div>

  <div class="summary-text-block">
    <p class="body-text">{market.market_size_summary}</p>
  </div>

  <div class="takeaways-block">
    <h4 class="sub-heading">Primary Growth Drivers</h4>
    <ul class="takeaways-list">
      {drivers_html}
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)

    @staticmethod
    def render_competitors_card(comp: CompetitorAnalysis) -> None:
        if not comp:
            return

        direct_html = "".join([
            f"<li><strong>{c.name}</strong> ({c.pricing_model}): {c.description}</li>"
            for c in comp.direct_competitors
        ])

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div>
      <div class="saas-card-label">COMPETITIVE ANALYSIS</div>
      <div class="saas-title">Competitive Landscape & Defensible Moat</div>
    </div>
  </div>

  <div class="summary-text-block">
    <p class="body-text"><strong>Market Positioning:</strong> {comp.market_positioning_summary}</p>
    <p class="body-text"><strong>Defensible Moat:</strong> {comp.moat_assessment}</p>
  </div>

  <div class="takeaways-block">
    <h4 class="sub-heading">Direct Competitors</h4>
    <ul class="takeaways-list">
      {direct_html or "<li>No major direct incumbents identified. First-mover advantage opportunity.</li>"}
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)

    @staticmethod
    def render_swot_risk_card(swot: SWOTAnalysis) -> None:
        if not swot:
            return

        risk_status, risk_cls = _get_score_status(swot.overall_risk_score, is_risk=True)

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div>
      <div class="saas-card-label">SWOT ANALYSIS</div>
      <div class="saas-title">SWOT Matrix & Risk Analysis</div>
    </div>
    <span class="metric-tag risk-tag">Overall Risk: {swot.overall_risk_score}/10 ({risk_status})</span>
  </div>

  <div class="swot-grid">
    <div class="swot-box swot-strengths">
      <h4 class="swot-header">Strengths</h4>
      <ul class="swot-list">
        {"".join([f"<li>{s}</li>" for s in swot.strengths])}
      </ul>
    </div>
    <div class="swot-box swot-weaknesses">
      <h4 class="swot-header">Weaknesses</h4>
      <ul class="swot-list">
        {"".join([f"<li>{w}</li>" for w in swot.weaknesses])}
      </ul>
    </div>
    <div class="swot-box swot-opportunities">
      <h4 class="swot-header">Opportunities</h4>
      <ul class="swot-list">
        {"".join([f"<li>{o}</li>" for o in swot.opportunities])}
      </ul>
    </div>
    <div class="swot-box swot-threats">
      <h4 class="swot-header">Threats</h4>
      <ul class="swot-list">
        {"".join([f"<li>{t}</li>" for t in swot.threats])}
      </ul>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    @staticmethod
    def render_mvp_card(mvp: MVPRecommendation) -> None:
        if not mvp:
            return

        feat_html = "".join([
            f"<li><strong>[{f.priority}] {f.feature_name}</strong> (~{f.estimated_days} days): {f.description}</li>"
            for f in mvp.features
        ])

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div>
      <div class="saas-card-label">MVP ROADMAP</div>
      <div class="saas-title">Minimum Viable Product (MVP) Blueprint</div>
    </div>
  </div>

  <div class="summary-text-block">
    <p class="body-text"><strong>Core Value Proposition:</strong> {mvp.core_value_proposition}</p>
  </div>

  <div class="architecture-box">
    <div class="arch-item"><span class="arch-label">Frontend</span><span class="arch-val">{mvp.tech_stack_frontend}</span></div>
    <div class="arch-item"><span class="arch-label">Backend</span><span class="arch-val">{mvp.tech_stack_backend}</span></div>
    <div class="arch-item"><span class="arch-label">AI Engine</span><span class="arch-val">{mvp.tech_stack_ai}</span></div>
    <div class="arch-item"><span class="arch-label">Database</span><span class="arch-val">{mvp.tech_stack_database}</span></div>
  </div>

  <div class="takeaways-block">
    <h4 class="sub-heading">Prioritized MVP Features</h4>
    <ul class="takeaways-list">
      {feat_html}
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)

    @staticmethod
    def render_gtm_card(gtm: GTMStrategy) -> None:
        if not gtm:
            return

        ch_html = "".join([f"<li>{c}</li>" for c in gtm.primary_acquisition_channels])

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div>
      <div class="saas-card-label">GO-TO-MARKET STRATEGY</div>
      <div class="saas-title">Go-To-Market Strategy & Pricing</div>
    </div>
  </div>

  <div class="summary-text-block">
    <p class="body-text"><strong>Positioning:</strong> {gtm.positioning_statement}</p>
    <p class="body-text"><strong>Pricing Architecture:</strong> {gtm.pricing_strategy}</p>
    <p class="body-text"><strong>CAC Estimate:</strong> {gtm.estimated_cac_summary}</p>
  </div>

  <div class="takeaways-block">
    <h4 class="sub-heading">Primary Customer Acquisition Channels</h4>
    <ul class="takeaways-list">
      {ch_html}
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)
