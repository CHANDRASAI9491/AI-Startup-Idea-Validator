import streamlit as st
from typing import Callable, Dict, Any


def render_idea_input_form(on_submit_callback: Callable[[Dict[str, Any]], None]) -> None:
    """Renders the clean SaaS Startup Idea Parameters Form Component."""
    st.markdown("""
<div class="saas-card parameters-card">
  <div class="saas-card-header">
    <div>
      <div class="saas-card-label">STARTUP PARAMETERS</div>
      <div class="saas-title">Startup Idea Parameters</div>
      <div class="saas-card-subtext">Tell us about your startup idea to get a comprehensive validation analysis.</div>
    </div>
  </div>
""", unsafe_allow_html=True)

    with st.form(key="startup_validation_form"):
        idea_text = st.text_area(
            "Startup Concept & Description",
            height=130,
            placeholder="Describe your startup concept, target customer problem, proposed solution, and key workflow...",
            help="Provide detail on your core value proposition for best validation accuracy."
        )

        col1, col2 = st.columns(2)
        with col1:
            target_industry = st.selectbox(
                "Target Industry",
                [
                    "Technology / SaaS",
                    "HealthTech & Digital Health",
                    "FinTech & InsurTech",
                    "AI & Machine Learning Platforms",
                    "E-Commerce & RetailTech",
                    "EdTech & Future of Work",
                    "Cybersecurity & Data Privacy",
                    "Developer Tools & Infrastructure",
                    "ClimateTech & CleanEnergy",
                    "Consumer App / Mobile"
                ]
            )
            target_audience = st.text_input(
                "Target Audience",
                value="Small & Medium Businesses (SMBs)"
            )

        with col2:
            business_model = st.selectbox(
                "Business Model",
                [
                    "B2B SaaS / Monthly Subscription",
                    "Freemium with Enterprise Tier",
                    "Usage-Based / API Consumption",
                    "Marketplace Transaction Fee",
                    "B2C Subscription",
                    "Direct Sales / Enterprise Contract"
                ]
            )
            budget = st.selectbox(
                "Estimated Initial Budget",
                ["Bootstrap ($5k - $25k)", "Seed ($25k - $100k)", "Venture Funded ($100k+)"]
            )

        timeline = st.selectbox(
            "Target Launch Timeline",
            ["1 - 3 Months", "3 - 6 Months", "6+ Months"]
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("Validate Startup", use_container_width=True)

        if submit_button:
            if not idea_text or len(idea_text.strip()) < 15:
                st.error("Please enter a detailed startup description (at least 15 characters) before submitting.")
            else:
                on_submit_callback({
                    "idea_text": idea_text.strip(),
                    "target_industry": target_industry,
                    "target_audience": target_audience,
                    "business_model": business_model,
                    "budget": budget,
                    "timeline": timeline
                })

    st.markdown("</div>", unsafe_allow_html=True)
