import html
import streamlit as st


def render_sidebar() -> str:
    """Renders the clean, compact sidebar navigation synchronized with application state."""
    with st.sidebar:
        sidebar_brand_html = (
            '<div class="sidebar-brand-container">'
            '<div class="sidebar-logo-mark">'
            '<div class="sidebar-logo-icon">V</div>'
            '<div>'
            '<div class="sidebar-logo-text">AI Startup Validator</div>'
            '<div class="sidebar-subtitle">SaaS Due Diligence Engine</div>'
            '</div>'
            '</div>'
            '</div>'
            '<div class="sidebar-divider"></div>'
        )
        st.markdown(sidebar_brand_html, unsafe_allow_html=True)

        nav_options = ["Validation", "History", "Reports", "Settings", "About"]
        current = st.session_state.get("current_page", "Validation")
        if current in ["Validate Startup", "Dashboard"]:
            current = "Validation"
        elif current in ["Validation History"]:
            current = "History"

        if current not in nav_options:
            current = "Validation"

        # Ensure radio key state stays synchronized with top navbar state
        if st.session_state.get("sidebar_navigation_radio") != current:
            st.session_state["sidebar_navigation_radio"] = current

        selected = st.radio(
            "Navigation",
            nav_options,
            index=nav_options.index(current),
            label_visibility="collapsed",
            key="sidebar_navigation_radio"
        )
        st.session_state.current_page = selected

        # Current Validation Session Card
        state = st.session_state.get("current_state")
        session_id = st.session_state.get("session_id")

        if state and getattr(state, "final_report", None):
            report = state.final_report
            startup_name = st.session_state.get("startup_name") or getattr(state.idea, "idea_text", "Active Venture")
            if len(startup_name) > 26:
                disp_name = startup_name[:23] + "..."
            else:
                disp_name = startup_name

            score = report.overall_viability_score
            verdict = report.verdict

            st.markdown(
                '<div class="sidebar-session-card">'
                '<div class="sidebar-session-label">ACTIVE SESSION</div>'
                f'<div class="sidebar-session-title" title="{html.escape(startup_name)}">{html.escape(disp_name)}</div>'
                f'<div class="sidebar-session-meta">'
                f'<span>Score: <strong>{score}/100</strong></span> &bull; '
                f'<span>{html.escape(verdict)}</span>'
                f'</div>'
                '</div>',
                unsafe_allow_html=True
            )

            col_new, col_adv = st.columns(2)
            with col_new:
                if st.button("New Analysis", key="sb_new_analysis", use_container_width=True, help="Clear active session and start a new validation"):
                    st.session_state.current_state = None
                    st.session_state.session_id = None
                    st.session_state.chat_history = []
                    st.session_state.startup_name = ""
                    st.session_state.current_page = "Validation"
                    st.rerun()
            with col_adv:
                adv_label = "Close Advisor" if st.session_state.get("advisor_open", False) else "AI Advisor"
                if st.button(adv_label, key="sb_toggle_advisor", use_container_width=True):
                    st.session_state.advisor_open = not st.session_state.get("advisor_open", False)
                    st.rerun()

        st.markdown("<div class='sidebar-divider' style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size: 11px; color: #94A3B8; text-align: center; padding: 4px 0;">'
            'Multi-Agent Due Diligence Platform<br/>v2.5 &bull; Powered by Deep Agents'
            '</div>',
            unsafe_allow_html=True
        )

        return selected
