import streamlit as st


def render_navbar(session_id: str = None, status: str = "Ready"):
    """Renders top header navigation status bar."""
    sess_display = session_id if session_id else "No active session"
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0 20px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 24px;">
            <div>
                <span style="font-size: 1.25rem; font-weight: 700; color: #0F172A; letter-spacing: -0.02em;">AI Startup Idea Validator</span>
                <span style="font-size: 0.8rem; color: #64748B; margin-left: 12px; background-color: #F1F5F9; padding: 3px 8px; border-radius: 4px; font-weight: 500;">Enterprise SaaS Edition</span>
            </div>
            <div style="font-size: 0.85rem; color: #475569;">
                <span style="margin-right: 16px;">Session: <strong style="color: #0F172A;">{sess_display}</strong></span>
                <span>System Status: <strong style="color: #166534; background-color: #DCFCE7; padding: 2px 8px; border-radius: 4px;">{status}</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
