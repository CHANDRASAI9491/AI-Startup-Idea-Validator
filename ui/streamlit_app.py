import streamlit as st
import json
import os
import sys

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.orchestrator import ApplicationOrchestrator
from state.schema import AgentState

# Page configuration
st.set_page_config(
    page_title="AI Startup Idea Validator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        margin-bottom: 15px;
    }

    /* Verdict Badge */
    .verdict-proceed {
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.2rem;
        display: inline-block;
    }
    .verdict-pivot {
        background: linear-gradient(135deg, #F59E0B, #D97706);
        color: white;
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.2rem;
        display: inline-block;
    }
    .verdict-caution {
        background: linear-gradient(135deg, #EF4444, #DC2626);
        color: white;
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.2rem;
        display: inline-block;
    }

    /* Custom Headers */
    .gradient-header {
        background: linear-gradient(90deg, #6366F1, #A855F7, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
    }

    .sub-header {
        color: #9CA3AF;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_orchestrator():
    return ApplicationOrchestrator()


orchestrator = get_orchestrator()

# Initialize session states
if "current_state" not in st.session_state:
    st.session_state.current_state = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Navigation
st.sidebar.markdown("### ⚡ AI Startup Validator")
st.sidebar.markdown("Validate startup concepts with real-time multi-agent market research.")

selected_page = st.sidebar.radio(
    "Navigation",
    ["🚀 Validate Idea", "📊 Executive Summary", "📈 Market Analysis", "⚔️ Competitors", "🛡️ SWOT & Risk", "🛠️ MVP & Tech", "🎯 GTM Strategy", "💬 AI Advisor Chat", "📜 History & Export"]
)

# Header
st.markdown('<h1 class="gradient-header">AI Startup Idea Validator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-agent AI platform evaluating TAM/SAM/SOM, competition, risk, MVP scope, and GTM strategy in seconds.</p>', unsafe_allow_html=True)

# PAGE 1: VALIDATE IDEA
if selected_page == "🚀 Validate Idea":
    st.markdown("### 📝 Enter Startup Concept")

    with st.form("validation_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            idea_text = st.text_area(
                "Startup Idea Description",
                placeholder="e.g. AI-powered B2B platform that automatically validates early-stage startup ideas using multi-agent web research and financial modeling.",
                height=120
            )
        with col2:
            target_industry = st.selectbox(
                "Target Industry",
                ["Technology / SaaS", "Artificial Intelligence", "FinTech", "HealthTech / BioTech", "E-commerce / Retail", "EdTech", "CleanTech", "Other"]
            )
            target_audience = st.text_input("Target Audience", value="Startup Founders, VCs & Product Managers")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            budget = st.selectbox("Estimated Budget", ["Bootstrap ($5k - $20k)", "Seed ($50k - $250k)", "Series A ($1M+)"])
        with col_b2:
            timeline = st.selectbox("Launch Timeline", ["1 Month", "3 Months", "6 Months"])

        submit_btn = st.form_submit_button("⚡ Validate Idea Now", type="primary")

    if submit_btn and idea_text:
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(step_id, status):
            step_map = {
                "web_search": (20, "🔍 Conducting Real-Time Web Research..."),
                "market_analysis": (40, "📈 Evaluating TAM/SAM/SOM & Market Size..."),
                "competitor_analysis": (55, "⚔️ Analyzing Competitor Matrix & Moats..."),
                "swot_risk": (70, "🛡️ Assessing SWOT & Calculating Risk Scores..."),
                "mvp_recommendation": (85, "🛠️ Scoping MVP Features & Tech Stack..."),
                "gtm_strategy": (92, "🎯 Formulating Go-To-Market Strategy..."),
                "final_report": (100, "🎯 Synthesizing Executive Report...")
            }
            if step_id in step_map:
                pct, msg = step_map[step_id]
                progress_bar.progress(pct)
                status_text.info(f"{msg} ({status.upper()})")

        with st.spinner("Executing Multi-Agent Validation Pipeline..."):
            state = orchestrator.validate_idea(
                idea_text=idea_text,
                target_industry=target_industry,
                target_audience=target_audience,
                budget=budget,
                timeline=timeline,
                progress_callback=update_progress
            )
            st.session_state.current_state = state
            st.session_state.session_id = state.idea.idea_text[:10]
            st.session_state.chat_history = []

        st.success("✅ Validation Complete! Select tabs on the left to view detailed analyses.")

# DISPLAY REPORT IF AVAILABLE
state: AgentState = st.session_state.current_state

if not state or not state.final_report:
    if selected_page != "🚀 Validate Idea" and selected_page != "📜 History & Export":
        st.info("👈 Please enter a startup idea in the '🚀 Validate Idea' tab to generate a validation report.")

else:
    report = state.final_report
    market = state.market_analysis
    comp = state.competitor_analysis
    swot = state.swot_analysis
    mvp = state.mvp_recommendation
    gtm = state.gtm_strategy

    # PAGE 2: EXECUTIVE SUMMARY
    if selected_page == "📊 Executive Summary":
        st.markdown("## 📊 Executive Validation Summary")

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.metric("Overall Viability Index", f"{report.overall_viability_score}/100")
        with col2:
            st.markdown(f"**Verdict:**")
            verdict_cls = "verdict-proceed" if report.verdict == "PROCEED" else ("verdict-pivot" if report.verdict == "PIVOT" else "verdict-caution")
            st.markdown(f'<div class="{verdict_cls}">{report.verdict}</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f"**Idea:** {state.idea.idea_text}")
            st.markdown(f"**Industry:** `{state.idea.target_industry}` | **Audience:** `{state.idea.target_audience}`")

        st.markdown("---")
        st.markdown("### 📝 Executive Overview")
        st.write(report.executive_summary)

        st.markdown("---")
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        m_col1.metric("Market Score", f"{report.market_score}/100")
        m_col2.metric("Competitor Score", f"{report.competitor_score}/100")
        m_col3.metric("Risk Resilience", f"{report.risk_score}/100")
        m_col4.metric("MVP Feasibility", f"{report.mvp_score}/100")
        m_col5.metric("GTM Potential", f"{report.gtm_score}/100")

        st.markdown("---")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("### 🔑 Key Takeaways")
            for t in report.key_takeaways:
                st.markdown(f"- ✅ {t}")
        with col_t2:
            st.markdown("### 🎯 Recommended Next Steps")
            for i, step in enumerate(report.recommended_next_steps, 1):
                st.markdown(f"**{i}.** {step}")

    # PAGE 3: MARKET ANALYSIS
    elif selected_page == "📈 Market Analysis" and market:
        st.markdown("## 📈 Market Analysis & Industry Sizing")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("TAM (Total Addressable)", f"${market.tam_billions}B")
        col2.metric("SAM (Serviceable)", f"${market.sam_billions}B")
        col3.metric("SOM (Obtainable)", f"${market.som_billions}B")
        col4.metric("Market CAGR %", f"{market.cagr_percentage}%")

        st.markdown("---")
        st.markdown("### 📜 Market Scope Summary")
        st.write(market.market_size_summary)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("### 🚀 Growth Drivers")
            for d in market.key_growth_drivers:
                st.markdown(f"- 📈 {d}")

        with col_g2:
            st.markdown("### 👤 Target Customer Personas")
            for persona in market.target_personas:
                st.markdown(f"**Role:** `{persona.role}`")
                st.markdown(f"- **Willingness to Pay:** {persona.willingness_to_pay}")
                st.markdown(f"- **Pain Points:** {', '.join(persona.pain_points)}")

    # PAGE 4: COMPETITORS
    elif selected_page == "⚔️ Competitors" and comp:
        st.markdown("## ⚔️ Competitor Analysis & Moat Assessment")
        st.markdown(f"**Market Positioning:** {comp.market_positioning_summary}")
        st.markdown(f"**Competitive Moat:** {comp.moat_assessment}")

        st.markdown("---")
        st.markdown("### 🎯 Direct Competitors")
        for competitor in comp.direct_competitors:
            with st.expander(f"🏢 {competitor.name} ({competitor.pricing_model})", expanded=True):
                st.write(competitor.description)
                if competitor.url:
                    st.markdown(f"🔗 [Website]({competitor.url})")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown("**Strengths:** " + ", ".join(competitor.strengths))
                with col_c2:
                    st.markdown("**Weaknesses:** " + ", ".join(competitor.weaknesses))

    # PAGE 5: SWOT & RISK
    elif selected_page == "🛡️ SWOT & Risk" and swot:
        st.markdown("## 🛡️ SWOT & Risk Matrix")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Financial Risk", f"{swot.financial_risk}/10")
        col2.metric("Technical Risk", f"{swot.technical_risk}/10")
        col3.metric("Regulatory Risk", f"{swot.regulatory_risk}/10")
        col4.metric("Overall Risk Score", f"{swot.overall_risk_score}/10")

        st.markdown("---")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("#### 💪 Strengths")
            for s in swot.strengths:
                st.markdown(f"- {s}")

            st.markdown("#### 🌟 Opportunities")
            for o in swot.opportunities:
                st.markdown(f"- {o}")

        with col_s2:
            st.markdown("#### ⚠️ Weaknesses")
            for w in swot.weaknesses:
                st.markdown(f"- {w}")

            st.markdown("#### 🚨 Threats")
            for t in swot.threats:
                st.markdown(f"- {t}")

        st.markdown("---")
        st.markdown("### 🛠️ Risk Mitigation Plan")
        for plan in swot.risk_mitigation_plan:
            st.markdown(f"- 🔒 {plan}")

    # PAGE 6: MVP & TECH
    elif selected_page == "🛠️ MVP & Tech" and mvp:
        st.markdown("## 🛠️ MVP Feature Scope & Recommended Tech Stack")
        st.info(f"**Core Value Proposition:** {mvp.core_value_proposition}")

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"**Frontend:** `{mvp.tech_stack_frontend}`")
        col2.markdown(f"**Backend:** `{mvp.tech_stack_backend}`")
        col3.markdown(f"**Database:** `{mvp.tech_stack_database}`")
        col4.markdown(f"**AI Engine:** `{mvp.tech_stack_ai}`")

        st.markdown("---")
        st.markdown("### 📋 Core Features")
        for feat in mvp.features:
            st.markdown(f"- **[{feat.priority}] {feat.feature_name}** ({feat.estimated_days} days) - {feat.description}")

        st.markdown("---")
        st.markdown("### 🗓️ 4-Week Development Roadmap")
        for week, desc in mvp.four_week_roadmap.items():
            st.markdown(f"**{week}:** {desc}")

    # PAGE 7: GTM STRATEGY
    elif selected_page == "🎯 GTM Strategy" and gtm:
        st.markdown("## 🎯 Go-To-Market Strategy")
        st.markdown(f"**Positioning:** {gtm.positioning_statement}")
        st.markdown(f"**Pricing Strategy:** {gtm.pricing_strategy}")
        st.markdown(f"**CAC Estimate:** {gtm.estimated_cac_summary}")

        st.markdown("---")
        st.markdown("### 📢 Primary Channels")
        for ch in gtm.primary_acquisition_channels:
            st.markdown(f"- 🚀 {ch}")

        st.markdown("### ⚡ Launch Tactics")
        for tactic in gtm.launch_tactics:
            st.markdown(f"- ✨ {tactic}")

    # PAGE 8: CHAT ADVISOR
    elif selected_page == "💬 AI Advisor Chat":
        st.markdown("## 💬 Interactive AI Startup Advisor")
        st.markdown("Ask follow-up questions to your AI Advisor grounded in your validation report findings.")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_q = st.chat_input("Ask a question about your startup strategy, market, or MVP...")
        if user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.write(user_q)

            with st.chat_message("assistant"):
                with st.spinner("Advisor thinking..."):
                    session_id = st.session_state.session_id or "default"
                    answer = orchestrator.ask_advisor(session_id, user_q, st.session_state.chat_history)
                    st.write(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

# PAGE 9: HISTORY & EXPORT
if selected_page == "📜 History & Export":
    st.markdown("## 📜 Past Validation History & Reports Export")

    sessions = orchestrator.list_all_sessions()
    if not sessions:
        st.info("No past validation sessions found.")
    else:
        for s in sessions:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.write(f"**Idea:** {s['idea']}")
            col2.write(f"**Score:** {s['score'] if s['score'] else 'N/A'}/100")
            col3.write(f"**Verdict:** {s['verdict'] if s['verdict'] else 'N/A'}")
            if col4.button("Load Report", key=s['session_id']):
                st.session_state.current_state = orchestrator.get_session_history(s['session_id'])
                st.session_state.session_id = s['session_id']
                st.success(f"Loaded session {s['session_id']}! Switch tabs to view.")

    if state and state.final_report:
        st.markdown("---")
        st.markdown("### 📥 Download Current Report")
        report_md = json.dumps(state.model_dump(), indent=2)
        st.download_button(
            label="Download JSON State Report",
            data=report_md,
            file_name=f"validation_report_{st.session_state.session_id}.json",
            mime="application/json"
        )
