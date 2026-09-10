import os
import base64
# pyrefly: ignore [missing-import]
import streamlit as st

HERO_SVG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images", "hero_analytics.svg"))
HERO_SVG_DATA_URI = ""
if os.path.exists(HERO_SVG_PATH):
    try:
        with open(HERO_SVG_PATH, "rb") as f:
            _b64 = base64.b64encode(f.read()).decode("utf-8")
            HERO_SVG_DATA_URI = f"data:image/svg+xml;base64,{_b64}"
    except Exception:
        pass


def render_top_navbar() -> None:
    """Deprecated: Top navigation removed in favor of clean sidebar navigation."""
    pass


def render_header(session_state=None) -> None:
    """Renders the clean, compact hero card with the requested messaging."""

    img_html = f'<img src="{HERO_SVG_DATA_URI}" class="hero-illustration-img" alt="Startup analytics illustration" style="max-width: 320px; width: 100%; height: auto; display: block; border-radius: 10px;" />' if HERO_SVG_DATA_URI else ''

    hero_html = (
        '<div class="saas-hero-container">'
        '<div class="hero-content">'
        '<div class="hero-badge-row">'
        '<span class="hero-eyebrow-badge">AI Venture Research &amp; Due Diligence</span>'
        '</div>'
        '<h1 class="saas-hero-heading">'
        'Turn your startup idea into a validated opportunity.'
        '</h1>'
        '<p class="saas-hero-subheading">'
        'Analyze market demand, competition, risks, and growth opportunities using AI-powered research.'
        '</p>'
        '</div>'
        f'<div class="hero-illustration-container">{img_html}</div>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)


def render_landing_view(on_start_validation=None, on_load_example=None) -> None:
    """Renders the primary landing view with hero, feature cards, and action buttons."""
    render_header()

    features_html = (
        '<div class="landing-features-grid">'
        '<div class="landing-feature-card">'
        '<div class="landing-feature-icon icon-market">&#128200;</div>'
        '<div class="landing-feature-title">Market Opportunity</div>'
        '<p class="landing-feature-desc">Evaluate TAM, SAM, and SOM projections with CAGR and growth driver analysis.</p>'
        '</div>'
        '<div class="landing-feature-card">'
        '<div class="landing-feature-icon icon-comp">&#9874;</div>'
        '<div class="landing-feature-title">Competitive Moat</div>'
        '<p class="landing-feature-desc">Map direct and indirect incumbents, feature matrices, and defensive differentiators.</p>'
        '</div>'
        '<div class="landing-feature-card">'
        '<div class="landing-feature-icon icon-risk">&#9888;</div>'
        '<div class="landing-feature-title">Risk &amp; SWOT</div>'
        '<p class="landing-feature-desc">Quantified probability and impact risk scoring with actionable mitigation strategies.</p>'
        '</div>'
        '<div class="landing-feature-card">'
        '<div class="landing-feature-icon icon-mvp">&#128640;</div>'
        '<div class="landing-feature-title">MVP &amp; Roadmap</div>'
        '<p class="landing-feature-desc">Prioritized V1 feature scope, modern architecture stack, and 4-week execution plan.</p>'
        '</div>'
        '</div>'
    )
    st.markdown(features_html, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Start Validation", key="landing_start_val_btn", type="primary", use_container_width=True):
            if on_start_validation:
                on_start_validation()
    with col2:
        if st.button("Load Example Idea", key="landing_load_ex_btn", use_container_width=True):
            if on_load_example:
                on_load_example()
