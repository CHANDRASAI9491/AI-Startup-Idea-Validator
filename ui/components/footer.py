import streamlit as st
from app.config import config


def render_footer() -> None:
    """Renders the clean System Footer."""
    st.markdown("---")
    st.markdown(f"""
<div style="text-align: center; font-size: 0.8rem; color: #94A3B8; padding: 1rem 0;">
  Development of AI Based Startup Idea Validator with Market Analysis Assistance
</div>
""", unsafe_allow_html=True)
