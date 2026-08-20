import streamlit as st


def render_idea_input_form(on_submit_callback) -> None:
    """Renders the clean SaaS Startup Idea Parameters input card."""
    st.markdown(
        '<div class="saas-card parameters-card">'
        '<div class="saas-card-header">'
        '<div>'
        '<div class="saas-card-label">STARTUP PARAMETERS</div>'
        '<div class="saas-title">Startup Idea Parameters</div>'
        '<div class="saas-card-subtext">Tell us about your startup idea to get a comprehensive validation analysis.</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    with st.form(key="startup_idea_form"):
        idea_text = st.text_area(
            "Startup Concept & Description",
            placeholder="Describe your product, the core problem it solves, and your primary value proposition...",
            height=120,
            help="Provide a clear, detailed overview of your startup idea."
        )

        col1, col2 = st.columns(2)

        with col1:
            target_industry = st.selectbox(
                "Target Industry",
                [
                    "Artificial Intelligence & ML",
                    "Fintech & Payments",
                    "Healthcare & Digital Health",
                    "E-Commerce & Retail",
                    "Enterprise SaaS",
                    "EdTech",
                    "Cybersecurity",
                    "CleanTech & Climate",
                    "Other"
                ]
            )

            target_audience = st.text_input(
                "Target Audience / ICP",
                placeholder="e.g. Early-stage B2B SaaS Founders, Series A startups",
                help="Who is the primary customer profile for this solution?"
            )

        with col2:
            business_model = st.selectbox(
                "Business Model",
                [
                    "B2B SaaS / Subscription",
                    "B2C Subscription",
                    "Usage-based / API",
                    "Marketplace / Transaction Fee",
                    "Enterprise Licensing",
                    "Freemium",
                    "Other"
                ]
            )

            budget = st.selectbox(
                "Initial Capital / Budget",
                ["Bootstrap (< $10k)", "$10k - $50k", "$50k - $250k", "$250k+"]
            )

        timeline = st.selectbox(
            "Target Launch Timeline",
            ["1 - 3 Months", "3 - 6 Months", "6+ Months"]
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("Validate Startup", use_container_width=True)

        if submit_button:
            if not idea_text or len(idea_text.strip()) < 15:
                st.error("Please provide a more detailed description of your startup idea (at least 15 characters).")
            else:
                on_submit_callback({
                    "idea_text": idea_text.strip(),
                    "target_industry": target_industry,
                    "target_audience": target_audience.strip() or "General Market",
                    "business_model": business_model,
                    "budget": budget,
                    "timeline": timeline
                })

    st.markdown("</div>", unsafe_allow_html=True)
