import streamlit as st
from ui.components.theme import (
    PRIMARY, SECONDARY, ACCENT, BACKGROUND, CARD_BG, TEXT, TEXT_MUTED,
    BORDER, SHADOW_CARD, BORDER_RADIUS, FONT_FAMILY
)


def inject_custom_css():
    """Injects high-quality Enterprise SaaS CSS into Streamlit with vibrant gradient headers and crisp white cards."""
    css = f"""
    <style>
        /* Main Application Background and Font */
        .stApp {{
            background-color: {BACKGROUND};
            color: {TEXT};
            font-family: {FONT_FAMILY};
        }}

        /* Main Container Padding */
        .main .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }}

        /* Enterprise Card Container */
        .saas-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: {SHADOW_CARD};
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }}

        .saas-card:hover {{
            border-color: #CBD5E1;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.06), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
        }}

        /* Gradient Headers */
        .gradient-title {{
            background: linear-gradient(90deg, {PRIMARY}, {SECONDARY}, {ACCENT});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.25rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            margin-bottom: 6px;
        }}

        .saas-subtitle {{
            font-size: 1.05rem;
            color: {TEXT_MUTED};
            margin-bottom: 24px;
            line-height: 1.5;
        }}

        .saas-section-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: {SECONDARY};
            letter-spacing: -0.015em;
            margin-bottom: 12px;
        }}

        /* Verdict Badges */
        .verdict-badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.95rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .verdict-proceed {{
            background-color: #DCFCE7;
            color: #166534;
            border: 1px solid #22C55E;
        }}
        .verdict-pivot {{
            background-color: #FEF08A;
            color: #854D0E;
            border: 1px solid #EAB308;
        }}
        .verdict-caution {{
            background-color: #FEE2E2;
            color: #991B1B;
            border: 1px solid #EF4444;
        }}

        /* Primary Form Action Button */
        .stButton > button {{
            background: linear-gradient(90deg, {PRIMARY}, {SECONDARY});
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 1rem;
            font-weight: 700;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.25);
            transition: all 0.15s ease;
        }}
        .stButton > button:hover {{
            background: linear-gradient(90deg, #1D4ED8, #6D28D9);
            box-shadow: 0 6px 12px -2px rgba(37, 99, 235, 0.35);
            color: #FFFFFF;
        }}

        /* Secondary Download Buttons */
        .stDownloadButton > button {{
            background-color: #FFFFFF;
            color: {TEXT};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }}
        .stDownloadButton > button:hover {{
            background-color: #F1F5F9;
            border-color: #CBD5E1;
            color: {TEXT};
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid {BORDER};
        }}

        /* Metric Box Styling */
        div[data-testid="stMetric"] {{
            background-color: #FFFFFF;
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 1px 3px 0 rgba(0,0,0,0.02);
        }}
        div[data-testid="stMetricLabel"] {{
            font-size: 0.85rem;
            color: {TEXT_MUTED};
            font-weight: 600;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.5rem;
            font-weight: 800;
            color: {PRIMARY};
        }}

        /* Chat Bubbles */
        .chat-bubble-user {{
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
            color: #1E40AF;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 12px;
            font-size: 0.95rem;
            line-height: 1.5;
        }}

        .chat-bubble-assistant {{
            background-color: #FFFFFF;
            border: 1px solid {BORDER};
            color: {TEXT};
            padding: 14px 18px;
            border-radius: 8px;
            margin-bottom: 16px;
            box-shadow: 0 1px 2px 0 rgba(0,0,0,0.03);
            font-size: 0.95rem;
            line-height: 1.5;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
