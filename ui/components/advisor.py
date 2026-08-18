import streamlit as st
from typing import Optional, List, Dict, Any

from state.schema import StartupState
from app.orchestrator import ApplicationOrchestrator
from app.config import config


def render_advisor_chat(
    orchestrator: ApplicationOrchestrator,
    state: Optional[StartupState],
) -> None:
    """Render the Grounded AI Venture Advisor floating launcher button and chat panel."""

    # ---------------------------------------------------------
    # SESSION STATE INITIALIZATION
    # ---------------------------------------------------------

    if "advisor_open" not in st.session_state:
        st.session_state.advisor_open = False

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ---------------------------------------------------------
    # FLOATING LAUNCHER BUTTON
    # ---------------------------------------------------------

    with st.container(key="floating_advisor_launcher"):
        icon = "✕" if st.session_state.advisor_open else "🤖"
        launcher_help = "Close Advisor" if st.session_state.advisor_open else "Open AI Venture Advisor"
        if st.button(
            icon,
            key="advisor_launcher_button",
            help=launcher_help,
        ):
            st.session_state.advisor_open = not st.session_state.advisor_open
            st.rerun()

    # If panel is closed, stop rendering panel elements
    if not st.session_state.advisor_open:
        return

    # ---------------------------------------------------------
    # HELPER: SUBMIT QUESTION TO ORCHESTRATOR
    # ---------------------------------------------------------

    def handle_question_submit(question_text: str) -> None:
        q_clean = question_text.strip()
        if not q_clean:
            return

        active_session_id = st.session_state.get("session_id")

        if not active_session_id or not state or not state.final_report:
            st.session_state.chat_history.append({"role": "user", "content": q_clean})
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "No active validation report found. Please validate a startup idea first."
            })
            st.rerun()
            return

        history_snapshot = list(st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "user", "content": q_clean})

        with st.spinner("AI Advisor analyzing report & web research..."):
            try:
                answer = orchestrator.ask_advisor(
                    session_id=active_session_id,
                    user_question=q_clean,
                    chat_history=history_snapshot,
                )
            except Exception as exc:
                answer = f"An error occurred while consulting the AI Advisor: {str(exc)}"

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    # ---------------------------------------------------------
    # FLOATING CHAT PANEL CONTAINER
    # ---------------------------------------------------------

    with st.container(key="floating_advisor_panel"):

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------
        col_title, col_clear, col_close = st.columns(
            [6, 1, 1],
            vertical_alignment="center",
        )

        with col_title:
            st.markdown("**🤖 Grounded AI Venture Advisor**")
            subtitle = "Report + Web Research" if config.is_tavily_available() else "Report-grounded strategic advice"
            st.caption(subtitle)

        with col_clear:
            if st.button("🗑️", key="advisor_clear", help="Clear chat history"):
                st.session_state.chat_history = []
                st.rerun()

        with col_close:
            if st.button("✕", key="advisor_close", help="Close chat panel"):
                st.session_state.advisor_open = False
                st.rerun()

        st.divider()

        # -----------------------------------------------------
        # ACTIVE STARTUP CONTEXT BADGE
        # -----------------------------------------------------
        active_session_id = st.session_state.get("session_id")
        has_active_report = bool(state and state.final_report and active_session_id)

        if has_active_report:
            idea_text = state.idea.idea_text or "Current startup concept"
            if len(idea_text) > 55:
                idea_text = idea_text[:52] + "..."
            st.info(f"📌 **Consulting on:** {idea_text}")
        else:
            st.warning("⚠️ **No active validation report.** Please validate a startup idea first.")

        # -----------------------------------------------------
        # CHAT MESSAGES AREA & WELCOME SUGGESTIONS
        # -----------------------------------------------------
        with st.container(height=390, border=False, key="advisor_messages"):
            if not st.session_state.chat_history:
                st.markdown("### 🤖 Hi! I'm your AI Venture Advisor.")
                st.caption(
                    "I can help you understand your validation report, risks, market, competitors, "
                    "MVP, GTM strategy, funding readiness, and current external market information."
                )

                st.caption("**Suggested questions**")

                suggested_questions = [
                    ("⚠️ What is the biggest risk?", "advisor_sq_risk"),
                    ("🏰 What is our strongest competitive advantage?", "advisor_sq_moat"),
                    ("📈 Is the market attractive enough?", "advisor_sq_market"),
                    ("🛠️ What should we build in the MVP?", "advisor_sq_mvp"),
                    ("🚀 How should we acquire our first customers?", "advisor_sq_gtm"),
                    ("⭐ How can we improve our viability score?", "advisor_sq_score"),
                    ("💼 What would investors question?", "advisor_sq_funding"),
                    ("🎯 What should we do next?", "advisor_sq_next"),
                ]

                for sq_text, sq_key in suggested_questions:
                    with st.container(key=sq_key):
                        if st.button(sq_text, key=f"btn_{sq_key}"):
                            handle_question_submit(sq_text)
            else:
                for msg in st.session_state.chat_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        with st.chat_message("user", avatar="👤"):
                            st.markdown(content)
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(content)

                # Render context-aware follow-up question suggestions below the latest assistant message
                if st.session_state.chat_history:
                    # Find last user question to determine intent
                    last_user_q = ""
                    for msg in reversed(st.session_state.chat_history):
                        if msg.get("role") == "user":
                            last_user_q = msg.get("content", "")
                            break

                    detected_intent = orchestrator.advisor.classify_intent(
                        last_user_q,
                        st.session_state.chat_history[:-2]
                    )

                    followup_map = {
                        "risk": [
                            ("🛡️ How can I reduce this risk?", "advisor_fu_1"),
                            ("🎯 Which risk should I address first?", "advisor_fu_2"),
                            ("⚠️ What would make this risk worse?", "advisor_fu_3"),
                        ],
                        "competition": [
                            ("💡 How can we differentiate?", "advisor_fu_1"),
                            ("🏰 What should our competitive moat be?", "advisor_fu_2"),
                            ("🎯 What competitor weakness can we exploit?", "advisor_fu_3"),
                        ],
                        "market": [
                            ("🔍 How can we validate the market further?", "advisor_fu_1"),
                            ("🎯 Which market segment should we target first?", "advisor_fu_2"),
                            ("📊 What current market trend matters most?", "advisor_fu_3"),
                        ],
                        "mvp": [
                            ("📦 What should be included in V1?", "advisor_fu_1"),
                            ("❌ What should we remove from the MVP?", "advisor_fu_2"),
                            ("💰 How can we reduce MVP development cost?", "advisor_fu_3"),
                        ],
                        "gtm": [
                            ("📢 Which acquisition channel should we test first?", "advisor_fu_1"),
                            ("📉 How can we reduce CAC?", "advisor_fu_2"),
                            ("🚀 What should our launch strategy be?", "advisor_fu_3"),
                        ],
                        "funding": [
                            ("💼 What would investors question?", "advisor_fu_1"),
                            ("📈 How can we improve investor readiness?", "advisor_fu_2"),
                            ("📊 What evidence should we collect before fundraising?", "advisor_fu_3"),
                        ],
                        "score": [
                            ("⭐ What would increase the score?", "advisor_fu_1"),
                            ("⚡ Which dimension is weakest?", "advisor_fu_2"),
                            ("🎯 What should we prioritize first?", "advisor_fu_3"),
                        ],
                        "general": [
                            ("🎯 What should I do next?", "advisor_fu_1"),
                            ("🚀 What is the biggest opportunity?", "advisor_fu_2"),
                            ("🔍 What should I validate next?", "advisor_fu_3"),
                        ],
                    }

                    followups = followup_map.get(detected_intent, followup_map["general"])

                    st.markdown("---")
                    st.caption("**Suggested follow-up questions**")
                    for fu_text, fu_key in followups:
                        with st.container(key=fu_key):
                            if st.button(fu_text, key=f"btn_{fu_key}_{len(st.session_state.chat_history)}"):
                                handle_question_submit(fu_text)

        # -----------------------------------------------------
        # QUESTION INPUT FORM (100% RELIABLE STREAMLIT PATTERN)
        # -----------------------------------------------------
        with st.form(key="advisor_input_form", clear_on_submit=True):
            col_in, col_btn = st.columns([5, 1], vertical_alignment="center")
            with col_in:
                user_question = st.text_input(
                    "Advisor Question",
                    placeholder="Ask about your market, competitors, risks, MVP, GTM, funding, or current trends...",
                    key="advisor_question_input",
                    label_visibility="collapsed",
                )
            with col_btn:
                submitted = st.form_submit_button("➤", help="Send question")

        if submitted and user_question.strip():
            handle_question_submit(user_question.strip())