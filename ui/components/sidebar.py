import streamlit as st


def render_sidebar() -> str:
    """Renders clean enterprise sidebar navigation without emojis."""
    st.sidebar.markdown("### Enterprise AI Platform")
    st.sidebar.markdown("<p style='font-size:0.85rem; color:#64748B;'>DeepAgents & LangGraph Validation Suite</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    selected_page = st.sidebar.radio(
        "Navigation Menu",
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

    st.sidebar.markdown("---")
    st.sidebar.markdown("<div style='font-size:0.75rem; color:#94A3B8;'>Enterprise System v2.0<br/>Status: Operational</div>", unsafe_allow_html=True)

    return selected_page
