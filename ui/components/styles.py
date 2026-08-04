import os
import streamlit as st


def inject_custom_css() -> None:
    """Injects the enterprise main.css stylesheet into Streamlit."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "main.css")
    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception:
            pass
