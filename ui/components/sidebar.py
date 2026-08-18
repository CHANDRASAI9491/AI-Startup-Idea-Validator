import streamlit as st


def render_sidebar() -> str:
    """Render the professional dark application sidebar."""

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand-container">
                <div class="sidebar-logo-mark">
                    <span class="sidebar-logo-pulse"></span>
                    <span class="sidebar-logo-text">Startup Validator</span>
                </div>
                <div class="sidebar-subtitle">
                    AI Venture Research & Due Diligence
                </div>
            </div>
            <div class="sidebar-divider"></div>
            """,
            unsafe_allow_html=True
        )

        page = st.radio(
            "Navigation",
            [
                "Validate Startup",
                "Reports",
                "Execution Status",
                "Settings",
                "About"
            ],
            index=0,
            label_visibility="collapsed"
        )

        return page