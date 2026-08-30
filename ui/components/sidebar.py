import streamlit as st


def render_sidebar() -> str:
    """Renders the dark sidebar navigation without Dashboard."""
    with st.sidebar:
        sidebar_brand_html = (
            '<div class="sidebar-brand-container">'
            '<div class="sidebar-logo-mark">'
            '<div class="sidebar-logo-icon">V</div>'
            '<div>'
            '<div class="sidebar-logo-text">Startup Validator</div>'
            '<div class="sidebar-subtitle">AI Venture Research & Due Diligence</div>'
            '</div>'
            '</div>'
            '</div>'
            '<div class="sidebar-divider"></div>'
        )
        st.markdown(sidebar_brand_html, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            [
                "Validate Startup",
                "Reports",
                "Settings",
                "About"
            ],
            index=0,
            label_visibility="collapsed"
        )

        return page