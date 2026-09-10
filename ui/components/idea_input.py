import streamlit as st


EXAMPLE_STARTUP = {
    "startup_name": "OmniPulse AI",
    "idea_text": (
        "Autonomous AI customer feedback intelligence platform that aggregates support tickets, "
        "app store reviews, community posts, and sales call transcripts to extract churn indicators, "
        "sentiment shifts, and feature requests to prioritize engineering roadmaps in real-time."
    ),
    "target_audience": "B2B SaaS Product Managers, Head of Support, and VP Engineering",
    "target_industry": "Enterprise SaaS",
    "business_model": "B2B SaaS / Subscription",
    "budget": "$10k - $50k",
    "timeline": "1 - 3 Months (Ideation / MVP)"
}


def load_example_startup_idea() -> None:
    """Populates the existing form fields with one fixed realistic example without auto-submitting."""
    st.session_state.startup_name = EXAMPLE_STARTUP["startup_name"]
    st.session_state.last_idea_text = EXAMPLE_STARTUP["idea_text"]
    st.session_state.last_target_audience = EXAMPLE_STARTUP["target_audience"]
    st.session_state.last_target_industry = EXAMPLE_STARTUP["target_industry"]
    st.session_state.last_business_model = EXAMPLE_STARTUP["business_model"]
    st.session_state.last_budget = EXAMPLE_STARTUP["budget"]
    st.session_state.last_timeline = EXAMPLE_STARTUP["timeline"]
    st.session_state.show_validation_form = True


def _safe_idx(options: list, val: str, default: int = 0) -> int:
    """Returns the index of a value in options or fallback default."""
    if val and val in options:
        return options.index(val)
    return default


def render_idea_input_form(on_submit_callback) -> None:
    """Renders the clean, visually organized SaaS Startup Idea Parameters input card."""
    col_hdr_title, col_hdr_action = st.columns([4.2, 1.8], vertical_alignment="center")
    with col_hdr_title:
        st.markdown(
            '<div class="saas-card-header" style="padding: 0 0 8px 0; margin-bottom: 0;">'
            '<div>'
            '<div class="saas-card-label">VENTURE DUE DILIGENCE ASSESSMENT</div>'
            '<div class="saas-title">Startup Idea Parameters</div>'
            '<div class="saas-card-subtext">Provide your venture details to generate an evidence-grounded due diligence report with real-time web research and deterministic scoring.</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col_hdr_action:
        if st.button("Load Example Idea", key="form_load_example_btn", use_container_width=True, help="Populate form with a realistic B2B SaaS example"):
            load_example_startup_idea()
            st.rerun()

    timeline_options = [
        "1 - 3 Months (Ideation / MVP)",
        "3 - 6 Months (Early Prototype)",
        "6+ Months (Scaling)"
    ]
    industry_options = [
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
    business_model_options = [
        "B2B SaaS / Subscription",
        "B2C Subscription",
        "Usage-based / API",
        "Marketplace / Transaction Fee",
        "Enterprise Licensing",
        "Freemium",
        "Other"
    ]
    budget_options = [
        "Bootstrap (< $10k)",
        "$10k - $50k",
        "$50k - $250k",
        "$250k+"
    ]

    selected_timeline_idx = _safe_idx(timeline_options, st.session_state.get("last_timeline", ""), default=0)
    selected_industry_idx = _safe_idx(industry_options, st.session_state.get("last_target_industry", ""), default=0)
    selected_bm_idx = _safe_idx(business_model_options, st.session_state.get("last_business_model", ""), default=0)
    selected_budget_idx = _safe_idx(budget_options, st.session_state.get("last_budget", ""), default=0)

    st.markdown('<div class="saas-card parameters-card" style="margin-top: 6px;">', unsafe_allow_html=True)

    with st.form(key="startup_idea_form"):
        col_name, col_stage = st.columns([1.2, 1])
        with col_name:
            startup_name = st.text_input(
                "Startup Name",
                value=st.session_state.get("startup_name", ""),
                placeholder="e.g. NextPulse AI, OmniFlow, LexiScan",
                help="Venture name used to brand your validation analysis and export reports."
            )
        with col_stage:
            timeline = st.selectbox(
                "Target Launch Timeline",
                timeline_options,
                index=selected_timeline_idx,
                help="Targeted launch window for your initial minimal viable product."
            )

        idea_text = st.text_area(
            "Startup Idea / Problem & Solution",
            value=st.session_state.get("last_idea_text", ""),
            placeholder="Describe the specific problem, proposed customer workflow, and primary value proposition for your target market...",
            height=135,
            help="Detail the customer friction, proposed mechanism, and unique value proposition."
        )

        col1, col2 = st.columns(2)

        with col1:
            target_audience = st.text_input(
                "Target Audience / ICP",
                value=st.session_state.get("last_target_audience", ""),
                placeholder="e.g. Early-stage B2B SaaS Founders, Series A engineering teams",
                help="Who is the primary customer profile or ideal buyer for this solution?"
            )

            target_industry = st.selectbox(
                "Industry Sector",
                industry_options,
                index=selected_industry_idx,
                help="Primary market category for competitive benchmarking."
            )

        with col2:
            business_model = st.selectbox(
                "Business Model",
                business_model_options,
                index=selected_bm_idx,
                help="Primary revenue and monetization model."
            )

            budget = st.selectbox(
                "Initial Capital / Budget",
                budget_options,
                index=selected_budget_idx,
                help="Estimated capital allocation for early validation and development."
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("Validate Startup", use_container_width=True)


        if submit_button:
            if not idea_text or len(idea_text.strip()) < 15:
                st.error("Please provide a more detailed description of your startup idea (at least 15 characters).")
            else:
                clean_name = startup_name.strip()
                clean_idea = idea_text.strip()
                if clean_name:
                    st.session_state.startup_name = clean_name

                st.session_state.last_idea_text = clean_idea
                st.session_state.last_target_audience = target_audience.strip()

                # Map timeline to standard backend value
                clean_timeline = "1 - 3 Months"
                if "1 - 3" in timeline:
                    clean_timeline = "1 - 3 Months"
                elif "3 - 6" in timeline:
                    clean_timeline = "3 - 6 Months"
                elif "6+" in timeline:
                    clean_timeline = "6+ Months"

                on_submit_callback({
                    "startup_name": clean_name,
                    "idea_text": clean_idea,
                    "target_industry": target_industry,
                    "target_audience": target_audience.strip() or "General Market",
                    "business_model": business_model,
                    "budget": budget,
                    "timeline": clean_timeline
                })

    st.markdown("</div>", unsafe_allow_html=True)
