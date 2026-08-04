import streamlit as st


def render_navbar(session_id: str = None, status: str = "Operational") -> None:
    """Renders the top status bar displaying session status."""
    session_text = f"Session ID: <code>{session_id}</code>" if session_id else "No Active Session"
    st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 1rem; background: #FFFFFF; border-bottom: 1px solid #E2E8F0; border-radius: 8px; margin-bottom: 1.5rem;">
  <div style="font-size: 0.875rem; color: #475569;">{session_text}</div>
  <div style="font-size: 0.875rem; color: #15803D; font-weight: 600;">Status: {status}</div>
</div>
""", unsafe_allow_html=True)
