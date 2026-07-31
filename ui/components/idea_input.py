import streamlit as st
from typing import Dict, Any, Optional
from ui.components.forms import render_startup_input_form


def render_idea_input_form(on_submit_callback) -> Optional[Dict[str, Any]]:
    """Renders the startup validation input form without Startup Name field."""
    return render_startup_input_form(on_submit_callback)
