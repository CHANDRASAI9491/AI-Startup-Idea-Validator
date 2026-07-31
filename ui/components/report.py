import streamlit as st
from state.schema import StartupState
from ui.components.cards import render_report_cards


def render_report_view(state: StartupState, session_id: str):
    """Component wrapper for rendering complete validation report cards."""
    if not state or not state.final_report:
        st.info("No active validation report found. Please input a startup concept on the main validation page.")
        return
    render_report_cards(state, session_id)
