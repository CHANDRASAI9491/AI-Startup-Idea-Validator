import streamlit as st


def render_header():
    """Renders main application header with gradient title and short description."""
    st.markdown('<div class="gradient-title">AI Startup Idea Validator</div>', unsafe_allow_html=True)
    st.markdown('<div class="saas-subtitle">Autonomous Enterprise Validation Engine powered by DeepAgents research planning and LangGraph multi-agent market analysis.</div>', unsafe_allow_html=True)
