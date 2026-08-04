import streamlit as st
from state.schema import StartupState, ValidationReport, MarketAnalysis, CompetitorAnalysis, SWOTAnalysis, MVPRecommendation, GTMStrategy


class CardComponents:
    """Reusable HTML/CSS Card Components for Enterprise Validation Dashboard."""

    @staticmethod
    def render_executive_summary_card(state: StartupState) -> None:
        report = state.final_report
        if not report:
            return

        scoring = report.scoring_breakdown
        verdict_class = f"badge-{report.verdict.lower()}"

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div class="saas-title">Executive Summary & Strategic Verdict</div>
    <span class="saas-badge {verdict_class}">{report.verdict}</span>
  </div>
  
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-value">{report.overall_viability_score}/100</div>
      <div class="metric-label">Overall Viability Score</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{report.investor_readiness_score}/100</div>
      <div class="metric-label">Investor Readiness</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{report.funding_probability}%</div>
      <div class="metric-label">Funding Probability</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{report.pmf_score}/100</div>
      <div class="metric-label">Product-Market Fit</div>
    </div>
  </div>

  <p style="font-size: 1.05rem; line-height: 1.6; color: #334155; margin-bottom: 1.25rem;">
    {report.executive_summary}
  </p>

  <h4 style="font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">Key Takeaways:</h4>
  <ul style="color: #475569; padding-left: 1.25rem; line-height: 1.6;">
    {"".join([f"<li>{t}</li>" for t in report.key_takeaways])}
  </ul>
</div>
""", unsafe_allow_html=True)

    @staticmethod
    def render_market_card(market: MarketAnalysis) -> None:
        if not market:
            return

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div class="saas-title">1. Market Sizing & CAGR Growth</div>
    <span style="font-weight: 700; color: #2563EB;">Readiness: {market.market_readiness_score}/100</span>
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
      <div class="metric-label">5-Year CAGR</div>
    </div>
  </div>

  <p style="color: #334155; line-height: 1.6;">{market.market_size_summary}</p>
  
  <h4 style="font-weight: 700; color: #0F172A; margin-top: 1rem; margin-bottom: 0.5rem;">Primary Growth Drivers:</h4>
  <ul style="color: #475569; padding-left: 1.25rem; line-height: 1.6;">
    {"".join([f"<li>{d}</li>" for d in market.key_growth_drivers])}
  </ul>
</div>
""", unsafe_allow_html=True)

    @staticmethod
    def render_competitors_card(comp: CompetitorAnalysis) -> None:
        if not comp:
            return

        direct_html = "".join([
            f"<li><b>{c.name}</b> ({c.pricing_model}): {c.description}</li>"
            for c in comp.direct_competitors
        ])

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div class="saas-title">2. Competitive Intelligence & Defensible Moat</div>
  </div>

  <p style="color: #334155; line-height: 1.6;"><b>Market Positioning:</b> {comp.market_positioning_summary}</p>
  <p style="color: #334155; line-height: 1.6;"><b>Defensible Moat:</b> {comp.moat_assessment}</p>

  <h4 style="font-weight: 700; color: #0F172A; margin-top: 1rem; margin-bottom: 0.5rem;">Direct Competitors:</h4>
  <ul style="color: #475569; padding-left: 1.25rem; line-height: 1.6;">
    {direct_html or "<li>No major direct incumbents identified. First mover opportunity.</li>"}
  </ul>
</div>
""", unsafe_allow_html=True)

    @staticmethod
    def render_swot_risk_card(swot: SWOTAnalysis) -> None:
        if not swot:
            return

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div class="saas-title">3. SWOT & Categorized Risk Profile</div>
    <span style="font-weight: 700; color: #EF4444;">Overall Risk: {swot.overall_risk_score}/10</span>
  </div>

  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
    <div style="background: #F0FDF4; padding: 1rem; border-radius: 8px; border: 1px solid #BBF7D0;">
      <h4 style="color: #15803D; margin-bottom: 0.5rem;">Strengths</h4>
      <ul style="padding-left: 1rem; color: #166534; font-size: 0.9rem;">
        {"".join([f"<li>{s}</li>" for s in swot.strengths])}
      </ul>
    </div>
    <div style="background: #FEF2F2; padding: 1rem; border-radius: 8px; border: 1px solid #FECACA;">
      <h4 style="color: #B91C1C; margin-bottom: 0.5rem;">Weaknesses</h4>
      <ul style="padding-left: 1rem; color: #991B1B; font-size: 0.9rem;">
        {"".join([f"<li>{w}</li>" for w in swot.weaknesses])}
      </ul>
    </div>
    <div style="background: #F0F9FF; padding: 1rem; border-radius: 8px; border: 1px solid #BAE6FD;">
      <h4 style="color: #0369A1; margin-bottom: 0.5rem;">Opportunities</h4>
      <ul style="padding-left: 1rem; color: #075985; font-size: 0.9rem;">
        {"".join([f"<li>{o}</li>" for o in swot.opportunities])}
      </ul>
    </div>
    <div style="background: #FFFBEB; padding: 1rem; border-radius: 8px; border: 1px solid #FDE68A;">
      <h4 style="color: #B45309; margin-bottom: 0.5rem;">Threats</h4>
      <ul style="padding-left: 1rem; color: #92400E; font-size: 0.9rem;">
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
            f"<li><b>[{f.priority}] {f.feature_name}</b> ({f.estimated_days} days): {f.description}</li>"
            for f in mvp.features
        ])

        st.markdown(f"""
<div class="saas-card">
  <div class="saas-card-header">
    <div class="saas-title">4. Minimum Viable Product (MVP) Blueprint</div>
  </div>

  <p style="color: #334155; line-height: 1.6;"><b>Core Value Proposition:</b> {mvp.core_value_proposition}</p>
  
  <div style="background: #F8FAFC; padding: 1rem; border-radius: 8px; margin: 1rem 0; font-size: 0.9rem; color: #475569;">
    <b>Recommended Architecture:</b><br/>
    • Frontend: {mvp.tech_stack_frontend}<br/>
    • Backend: {mvp.tech_stack_backend}<br/>
    • AI Engine: {mvp.tech_stack_ai}<br/>
    • Database: {mvp.tech_stack_database}
  </div>

  <h4 style="font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">Prioritized MVP Features:</h4>
  <ul style="color: #475569; padding-left: 1.25rem; line-height: 1.6;">
    {feat_html}
  </ul>
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
    <div class="saas-title">5. Go-To-Market & Pricing Strategy</div>
  </div>

  <p style="color: #334155; line-height: 1.6;"><b>Positioning:</b> {gtm.positioning_statement}</p>
  <p style="color: #334155; line-height: 1.6;"><b>Pricing Architecture:</b> {gtm.pricing_strategy}</p>

  <h4 style="font-weight: 700; color: #0F172A; margin-top: 1rem; margin-bottom: 0.5rem;">Primary Customer Acquisition Channels:</h4>
  <ul style="color: #475569; padding-left: 1.25rem; line-height: 1.6;">
    {ch_html}
  </ul>
</div>
""", unsafe_allow_html=True)
