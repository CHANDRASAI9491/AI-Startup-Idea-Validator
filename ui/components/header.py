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
    """Renders the professional modern AI SaaS top navigation bar."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Validation"

    st.markdown('<div class="saas-top-navbar-wrapper">', unsafe_allow_html=True)
    col_brand, col_nav = st.columns([3.4, 6.6], vertical_alignment="center")

    with col_brand:
        st.markdown(
            '<div class="top-nav-brand">'
            '<div class="brand-logo-gem">V</div>'
            '<div>'
            '<span class="brand-name">AI Startup Idea Validator</span>'
            '<span class="brand-badge">SaaS Due Diligence Platform</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with col_nav:
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1.5], vertical_alignment="center")
        curr = st.session_state.get("current_page", "Validation")

        with c1:
            val_type = "primary" if curr == "Validation" else "secondary"
            if st.button("Validation", key="nav_btn_val", use_container_width=True, type=val_type):
                st.session_state.current_page = "Validation"
                st.rerun()

        with c2:
            hist_type = "primary" if curr == "History" else "secondary"
            if st.button("History", key="nav_btn_hist", use_container_width=True, type=hist_type):
                st.session_state.current_page = "History"
                st.rerun()

        with c3:
            rep_type = "primary" if curr == "Reports" else "secondary"
            if st.button("Reports", key="nav_btn_rep", use_container_width=True, type=rep_type):
                st.session_state.current_page = "Reports"
                st.rerun()

        with c4:
            set_type = "primary" if curr == "Settings" else "secondary"
            if st.button("Settings", key="nav_btn_set", use_container_width=True, type=set_type):
                st.session_state.current_page = "Settings"
                st.rerun()

        with c5:
            adv_open = st.session_state.get("advisor_open", False)
            adv_type = "primary" if adv_open else "secondary"
            if st.button("AI Venture Advisor", key="nav_btn_adv", use_container_width=True, type=adv_type):
                st.session_state.advisor_open = not st.session_state.get("advisor_open", False)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_header(session_state=None) -> None:
    """Renders the top navbar and the clean, compact hero card with the requested messaging."""
    render_top_navbar()

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
