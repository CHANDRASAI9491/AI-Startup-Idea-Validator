import streamlit as st
from typing import Dict, Any, Optional


def render_startup_input_form(on_submit_callback) -> Optional[Dict[str, Any]]:
    """Renders the startup validation input form without Startup Name field."""
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="saas-section-title">Startup Idea Input Form</div>', unsafe_allow_html=True)
    st.markdown('<div class="saas-subtitle">Specify your startup concept description, target industry, customer segment, business model, budget, and launch timeline. DeepAgents and LangGraph will execute multi-agent validation.</div>', unsafe_allow_html=True)

    # Initialize default session state values if missing
    if "form_idea_text" not in st.session_state:
        st.session_state.form_idea_text = ""
    if "form_target_industry" not in st.session_state:
        st.session_state.form_target_industry = "Technology / SaaS"
    if "form_target_audience" not in st.session_state:
        st.session_state.form_target_audience = "Startup Founders, VCs, and Product Managers"
    if "form_business_model" not in st.session_state:
        st.session_state.form_business_model = "B2B SaaS / Subscription"
    if "form_budget" not in st.session_state:
        st.session_state.form_budget = "Bootstrap ($5k - $50k)"
    if "form_timeline" not in st.session_state:
        st.session_state.form_timeline = "3 Months"

    with st.form("enterprise_startup_form"):
        idea_text = st.text_area(
            "Startup Description",
            value=st.session_state.form_idea_text,
            placeholder="Provide a detailed description of your startup concept, core customer problem, primary feature workflow, and target value proposition...",
            height=150
        )

        col_i1, col_i2 = st.columns([1, 1])
        with col_i1:
            target_industry = st.selectbox(
                "Industry Sector",
                [
                    "Technology / SaaS",
                    "Artificial Intelligence",
                    "FinTech",
                    "HealthTech / BioTech",
                    "E-commerce / Retail",
                    "EdTech",
                    "CleanTech",
                    "Enterprise Software",
                    "LegalTech",
                    "Other"
                ],
                index=0
            )
        with col_i2:
            target_audience = st.text_input(
                "Target Customers (Optional)",
                value=st.session_state.form_target_audience,
                placeholder="e.g. Enterprise Legal Teams & Law Firms"
            )

        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            business_model = st.text_input(
                "Business Model (Optional)",
                value=st.session_state.form_business_model,
                placeholder="e.g. Tiered Monthly SaaS Subscription"
            )
        with col_m2:
            budget = st.selectbox(
                "Estimated Initial Budget",
                ["Bootstrap ($5k - $50k)", "Seed ($50k - $250k)", "Series A ($1M+)"]
            )

        timeline = st.selectbox(
            "Target Launch Timeline",
            ["1 Month", "3 Months", "6 Months"]
        )

        submit_btn = st.form_submit_button("Validate Startup Concept", use_container_width=True)

    if submit_btn:
        if not idea_text or not idea_text.strip():
            st.error("Please provide a valid Startup Description before submitting.")
            return None

        # Bind parameters to session state so user input is preserved across rerenders
        st.session_state.form_idea_text = idea_text
        st.session_state.form_target_industry = target_industry
        st.session_state.form_target_audience = target_audience
        st.session_state.form_business_model = business_model
        st.session_state.form_budget = budget
        st.session_state.form_timeline = timeline

        form_data = {
            "idea_text": idea_text,
            "target_industry": target_industry,
            "target_audience": target_audience,
            "business_model": business_model,
            "budget": budget,
            "timeline": timeline
        }
        
        on_submit_callback(form_data)
        return form_data

    st.markdown('</div>', unsafe_allow_html=True)
    return None
