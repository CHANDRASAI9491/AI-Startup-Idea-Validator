import streamlit as st
from app.config import config


def render_sidebar() -> str:
    """Render the main application sidebar."""

    with st.sidebar:

        st.markdown(
            f"## {config.APP_NAME}"
        )

        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "Validate Startup",
                "Reports",
                "AI Advisor",
                "Execution Status",
                "Settings",
                "About"
            ],
            index=0
        )

        return page