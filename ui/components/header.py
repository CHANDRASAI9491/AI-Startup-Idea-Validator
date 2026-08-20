import os
import base64
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
    """Renders the dark top navigation bar."""
    navbar_html = (
        '<div class="saas-top-navbar">'
        '<div class="top-nav-left">'
        '<div class="top-nav-brand">'
        '<div class="brand-logo-gem">V</div>'
        '<span class="brand-name">Startup Validator</span>'
        '</div>'
        '</div>'
        '<div class="top-nav-right">'
        '<span class="top-nav-link">Reports</span>'
        '<span class="top-nav-link">Settings</span>'
        '<span class="top-nav-link">About</span>'
        '</div>'
        '</div>'
    )
    st.markdown(navbar_html, unsafe_allow_html=True)


def render_header(session_state=None) -> None:
    """Renders the top navbar and the clean light hero card with base64 encoded illustration image."""
    render_top_navbar()

    img_html = f'<img src="{HERO_SVG_DATA_URI}" class="hero-illustration-img" alt="Startup analytics illustration" style="max-width: 380px; width: 100%; height: auto; display: block; border-radius: 12px;" />' if HERO_SVG_DATA_URI else ''

    hero_html = (
        '<div class="saas-hero-container">'
        '<div class="hero-content">'
        '<div class="hero-badge-row">'
        '<span class="hero-eyebrow-badge">AI Venture Research &amp; Due Diligence</span>'
        '</div>'
        '<h1 class="saas-hero-heading">'
        'Development of AI Based Startup Idea Validator<br/>'
        '<span class="hero-subtext">with Market Analysis Assistance</span>'
        '</h1>'
        '<p class="saas-hero-subheading">'
        'Turn your idea into an evidence-based startup validation report.'
        '</p>'
        '</div>'
        f'<div class="hero-illustration-container">{img_html}</div>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)
