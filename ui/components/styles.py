import os
import streamlit as st

STYLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles")


def inject_custom_css():
    """Reads and injects global CSS files from ui/styles/ (theme.css, style.css, animations.css) into Streamlit."""
    theme_path = os.path.join(STYLES_DIR, "theme.css")
    style_path = os.path.join(STYLES_DIR, "style.css")
    anim_path = os.path.join(STYLES_DIR, "animations.css")

    css_contents = []

    for path in [theme_path, style_path, anim_path]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                css_contents.append(f.read())

    combined_css = "\n".join(css_contents)
    st.markdown(f"<style>\n{combined_css}\n</style>", unsafe_allow_html=True)
