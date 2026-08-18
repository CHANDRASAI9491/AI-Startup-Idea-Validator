import os
import streamlit as st


def inject_custom_css() -> None:
    """Injects custom CSS stylesheets into Streamlit."""
    styles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "styles"))
    for css_filename in ["style.css", "main.css", "advisor.css"]:
        css_path = os.path.join(styles_dir, css_filename)
        if os.path.exists(css_path):
            try:
                with open(css_path, "r", encoding="utf-8") as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            except Exception:
                pass

