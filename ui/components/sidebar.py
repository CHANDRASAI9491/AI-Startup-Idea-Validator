import streamlit as st


def render_sidebar() -> str:
    """Renders the dark sidebar navigation synchronized with application state."""
    with st.sidebar:
        sidebar_brand_html = (
            '<div class="sidebar-brand-container">'
            '<div class="sidebar-logo-mark">'
            '<div class="sidebar-logo-icon">V</div>'
            '<div>'
            '<div class="sidebar-logo-text">AI Startup Idea Validator</div>'
            '<div class="sidebar-subtitle">AI Venture Intelligence Platform</div>'
            '</div>'
            '</div>'
            '</div>'
            '<div class="sidebar-divider"></div>'
        )
        st.markdown(sidebar_brand_html, unsafe_allow_html=True)

        nav_options = ["Validation", "History", "Reports", "Settings", "About"]
        current = st.session_state.get("current_page", "Validation")
        if current in ["Validate Startup", "Dashboard"]:
            current = "Validation"
        elif current in ["Validation History"]:
            current = "History"

        default_idx = nav_options.index(current) if current in nav_options else 0

        selected = st.radio(
            "Navigation",
            nav_options,
            index=default_idx,
            label_visibility="collapsed",
            key="sidebar_navigation_radio"
        )
        st.session_state.current_page = selected
        return selected
