import streamlit as st
from app.config import config


def render_sidebar() -> str:
    """Renders the Enterprise Sidebar Navigation Menu."""
    with st.sidebar:
        st.markdown(f"### {config.APP_NAME}")
        st.markdown(f"*Version {config.APP_VERSION}*")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["Validate Startup", "Reports", "AI Advisor", "Execution Status", "Settings", "About"],
            index=0
        )

        st.markdown("---")
        st.markdown("#### Engine Status")
        st.markdown(f"• **Gemini AI:** `{'Ready' if config.is_gemini_available() else 'Fallback Mode'}`")
        st.markdown(f"• **Tavily Search:** `{'Ready' if config.is_tavily_available() else 'Structured Fallback'}`")
        st.markdown(f"• **Orchestrator:** `LangGraph + DeepAgents`")

        return page
