import streamlit as st


def render_footer():
    """Renders enterprise SaaS footer."""
    st.markdown(
        """
        <div style="margin-top: 48px; padding-top: 20px; border-top: 1px solid #E2E8F0; display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #64748B;">
            <div>
                © 2026 AI Startup Idea Validator. Built with Clean Architecture, DeepAgents, and LangGraph.
            </div>
            <div>
                Enterprise SaaS Platform | All Rights Reserved
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
