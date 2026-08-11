import streamlit as st


def render_header() -> None:
    """Renders the Hero Banner Section for the AI Startup Idea Validator Home Page."""
    st.markdown("""
<div class="hero-container">
  <div class="hero-badge">DeepAgents + LangGraph Multi-Agent Architecture</div>
  <div class="hero-title">Development of AI Based Startup Idea Validator with Market Analysis Assistance</div>
  <div class="hero-subtitle">
    Transform early-stage startup concepts into investor-ready strategic validation reports with Tavily web research, deterministic 8-dimension scoring, and grounded AI decision support.
  </div>
</div>
""", unsafe_allow_html=True)
