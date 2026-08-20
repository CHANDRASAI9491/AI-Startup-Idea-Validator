import os
import base64
import streamlit as st
from typing import Optional, List, Dict, Any

from state.schema import StartupState
from app.orchestrator import ApplicationOrchestrator
from app.config import config
from database.chat_history import (
    initialize_database,
    create_conversation,
    get_conversation,
    list_conversations,
    delete_conversation,
    save_message,
    get_messages,
    update_conversation_title,
    generate_title_from_message,
)

# Load custom SVG icon
ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images", "ai_advisor_icon.svg"))
SVG_ICON_DATA_URI = ""
if os.path.exists(ICON_PATH):
    try:
        with open(ICON_PATH, "r", encoding="utf-8") as f:
            _svg_text = f.read()
            _b64 = base64.b64encode(_svg_text.encode("utf-8")).decode("utf-8")
            SVG_ICON_DATA_URI = f"data:image/svg+xml;base64,{_b64}"
    except Exception:
        pass


def render_advisor_chat(
    orchestrator: ApplicationOrchestrator,
    state: Optional[StartupState],
) -> None:
    """Render the Grounded AI Venture Advisor with persistent SQLite chat history and a custom SVG icon."""

    # ---------------------------------------------------------
    # 1. DATABASE & STATE SYNCHRONIZATION
    # ---------------------------------------------------------
    try:
        initialize_database()
    except Exception as e:
        st.warning(f"Database initialization warning: {e}")

    if "advisor_open" not in st.session_state:
        st.session_state.advisor_open = False

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = None

    # Resolve active StartupState from argument or session state or orchestrator memory
    current_state: Optional[StartupState] = state or st.session_state.get("current_state")
    current_session_id: Optional[str] = st.session_state.get("session_id")

    if not current_state and current_session_id:
        current_state = orchestrator.get_session_history(current_session_id)
        if current_state:
            st.session_state.current_state = current_state

    # Ensure current state is synced to orchestrator memory under session_id
    if current_state and current_state.final_report:
        if not current_session_id:
            import uuid
            current_session_id = f"session_{str(uuid.uuid4())[:8]}"
            st.session_state.session_id = current_session_id
        orchestrator.memory.save_state(current_session_id, current_state)

    # Validate or initialize active_conversation_id
    conv_list = list_conversations()
    active_conv_id = st.session_state.active_conversation_id

    if active_conv_id:
        existing_conv = get_conversation(active_conv_id)
        if not existing_conv:
            active_conv_id = None

    if not active_conv_id:
        if conv_list:
            active_conv_id = conv_list[0]["id"]
        else:
            active_conv_id = create_conversation(
                title="New Conversation",
                session_id=current_session_id
            )
            conv_list = list_conversations()
        st.session_state.active_conversation_id = active_conv_id

    # Load messages from SQLite for the active conversation
    if active_conv_id:
        persisted_msgs = get_messages(active_conv_id)
        st.session_state.chat_history = [
            {"role": m["role"], "content": m["content"]} for m in persisted_msgs
        ]

    # ---------------------------------------------------------
    # 2. FLOATING 60PX CIRCULAR LAUNCHER (BOTTOM-RIGHT)
    # ---------------------------------------------------------
    with st.container(key="floating_advisor_launcher"):
        launcher_help = "Close Advisor" if st.session_state.advisor_open else "AI Venture Advisor"
        if st.button(
            "",
            key="advisor_launcher_button",
            help=launcher_help,
        ):
            st.session_state.advisor_open = not st.session_state.advisor_open
            st.rerun()

    # If drawer is closed, do not render panel
    if not st.session_state.advisor_open:
        return

    # ---------------------------------------------------------
    # 3. HELPER: QUESTION SUBMISSION
    # ---------------------------------------------------------
    def handle_question_submit(question_text: str) -> None:
        q_clean = question_text.strip()
        if not q_clean:
            return

        curr_conv_id = st.session_state.get("active_conversation_id")
        if not curr_conv_id:
            curr_conv_id = create_conversation(
                title="New Conversation",
                session_id=st.session_state.get("session_id")
            )
            st.session_state.active_conversation_id = curr_conv_id

        # Re-resolve active state
        rep_state = state or st.session_state.get("current_state")
        rep_sess_id = st.session_state.get("session_id")

        if not rep_state and rep_sess_id:
            rep_state = orchestrator.get_session_history(rep_sess_id)

        # Check if conversation is associated with a specific session_id in SQLite
        conv_meta = get_conversation(curr_conv_id)
        if conv_meta and conv_meta.get("session_id"):
            conv_sess_id = conv_meta.get("session_id")
            saved_state = orchestrator.get_session_history(conv_sess_id)
            if saved_state and saved_state.final_report:
                rep_state = saved_state
                rep_sess_id = conv_sess_id

        if not rep_state or not rep_state.final_report:
            try:
                save_message(curr_conv_id, "user", q_clean)
                save_message(
                    curr_conv_id,
                    "assistant",
                    "No active validation report is available. Please validate a startup idea first."
                )
            except Exception:
                pass
            st.rerun()
            return

        # Ensure session is registered in memory
        if not rep_sess_id:
            import uuid
            rep_sess_id = f"session_{str(uuid.uuid4())[:8]}"
            st.session_state.session_id = rep_sess_id
        orchestrator.memory.save_state(rep_sess_id, rep_state)

        # 1. Save user message to SQLite
        try:
            save_message(curr_conv_id, "user", q_clean)
        except Exception:
            pass

        # 2. Update conversation title if default
        if conv_meta and (conv_meta.get("title") in ["New Conversation", "Untitled Chat", ""] or not conv_meta.get("title")):
            new_title = generate_title_from_message(q_clean)
            update_conversation_title(curr_conv_id, new_title)

        # 3. Retrieve bounded history (up to 20 messages in chronological order)
        history_msgs = get_messages(curr_conv_id, limit=20)
        history_snapshot = [{"role": m["role"], "content": m["content"]} for m in history_msgs]

        # 4. Check if query triggers web search
        intent = orchestrator.advisor.classify_intent(q_clean, history_snapshot)
        report_context = orchestrator.advisor.build_intent_context(intent, rep_state)
        needs_web = orchestrator.advisor.should_search_web(q_clean, intent, report_context)

        spinner_text = "Researching current market information..." if needs_web else "Analyzing report & evidence..."

        with st.spinner(spinner_text):
            try:
                answer = orchestrator.ask_advisor(
                    session_id=rep_sess_id,
                    user_question=q_clean,
                    chat_history=history_snapshot,
                )
            except Exception as exc:
                answer = f"An error occurred while consulting the AI Advisor: {str(exc)}"

        if not answer or not answer.strip():
            answer = "I apologize, but I could not generate a response. Please try rephrasing your question."

        # 5. Save assistant answer to SQLite
        try:
            save_message(curr_conv_id, "assistant", answer)
        except Exception:
            pass

        st.rerun()

    # ---------------------------------------------------------
    # 4. COMPACT FLOATING DRAWER PANEL CONTAINER
    # ---------------------------------------------------------
    with st.container(key="floating_advisor_panel"):

        # -----------------------------------------------------
        # A. HEADER BAR
        # -----------------------------------------------------
        col_hdr, col_close = st.columns([5.5, 1.2], vertical_alignment="center")

        with col_hdr:
            icon_img_html = f"<img src='{SVG_ICON_DATA_URI}' style='width: 22px; height: 22px; margin-right: 8px; vertical-align: middle;' />" if SVG_ICON_DATA_URI else ""
            hdr_html = (
                '<div style="display: flex; align-items: center;">'
                f'{icon_img_html}'
                '<div>'
                '<div class="advisor-header-title">AI Venture Advisor</div>'
                f'<div class="advisor-header-status">{"Report active" if (current_state and current_state.final_report) else "No active validation report"}</div>'
                '</div>'
                '</div>'
            )
            st.markdown(hdr_html, unsafe_allow_html=True)

        with col_close:
            if st.button("Close", key="advisor_close", help="Close Advisor drawer"):
                st.session_state.advisor_open = False
                st.rerun()

        # -----------------------------------------------------
        # B. CHAT HISTORY CONTROLS
        # -----------------------------------------------------
        st.markdown("<div class='chat-history-section-header'>CHAT HISTORY</div>", unsafe_allow_html=True)
        conv_list = list_conversations()
        
        col_sel, col_new, col_del = st.columns([4.0, 2.2, 1.6], vertical_alignment="center")

        with col_sel:
            if conv_list:
                conv_ids = [c["id"] for c in conv_list]
                curr_id = st.session_state.get("active_conversation_id")
                sel_idx = conv_ids.index(curr_id) if curr_id in conv_ids else 0

                def format_label(cid: str) -> str:
                    match = next((c for c in conv_list if c["id"] == cid), None)
                    if match:
                        t = match.get("title", "Conversation")
                        if len(t) > 26:
                            t = t[:23] + "..."
                        return t
                    return "Conversation"

                selected_conv_id = st.selectbox(
                    "Select Conversation",
                    options=conv_ids,
                    index=sel_idx,
                    format_func=format_label,
                    key="advisor_conversation_selector",
                    label_visibility="collapsed"
                )

                if selected_conv_id != st.session_state.get("active_conversation_id"):
                    st.session_state.active_conversation_id = selected_conv_id
                    st.session_state.chat_history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in get_messages(selected_conv_id)
                    ]
                    st.rerun()

        with col_new:
            if st.button("+ New Chat", key="advisor_new_chat", help="Start a new chat"):
                # Check if current conversation is already an empty New Conversation
                curr_id = st.session_state.get("active_conversation_id")
                curr_msgs = get_messages(curr_id) if curr_id else []
                curr_meta = get_conversation(curr_id) if curr_id else None

                if curr_id and len(curr_msgs) == 0 and curr_meta and curr_meta.get("title") == "New Conversation":
                    # Already on a clean empty conversation, no need to create duplicate
                    st.session_state.chat_history = []
                else:
                    new_id = create_conversation(
                        title="New Conversation",
                        session_id=st.session_state.get("session_id")
                    )
                    st.session_state.active_conversation_id = new_id
                    st.session_state.chat_history = []
                st.rerun()

        with col_del:
            with st.popover("Delete", help="Delete current conversation"):
                st.markdown("<p style='font-size: 11px; margin-bottom: 6px; font-weight: 600; color: #0F172A;'>Delete this chat?</p>", unsafe_allow_html=True)
                if st.button("Confirm Delete", key="advisor_confirm_delete", type="primary"):
                    curr_id = st.session_state.get("active_conversation_id")
                    if curr_id:
                        delete_conversation(curr_id)
                    remaining = list_conversations()
                    if remaining:
                        st.session_state.active_conversation_id = remaining[0]["id"]
                        st.session_state.chat_history = [
                            {"role": m["role"], "content": m["content"]}
                            for m in get_messages(remaining[0]["id"])
                        ]
                    else:
                        new_id = create_conversation(
                            title="New Conversation",
                            session_id=st.session_state.get("session_id")
                        )
                        st.session_state.active_conversation_id = new_id
                        st.session_state.chat_history = []
                    st.rerun()

        st.markdown("<div class='advisor-divider'></div>", unsafe_allow_html=True)

        # -----------------------------------------------------
        # C. ACTIVE REPORT CONTEXT BADGE
        # -----------------------------------------------------
        if current_state and current_state.final_report:
            concept_text = current_state.idea.idea_text or "Current startup concept"
            if len(concept_text) > 48:
                concept_text = concept_text[:45] + "..."
            st.markdown(f"<div class='context-badge'><strong>Consulting on:</strong> {concept_text}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='context-badge warning'><strong>No active validation report.</strong> Validate an idea first.</div>", unsafe_allow_html=True)

        # -----------------------------------------------------
        # D. SCROLLABLE MESSAGES CONTAINER
        # -----------------------------------------------------
        with st.container(height=320, border=False, key="advisor_messages"):
            if not st.session_state.chat_history:
                st.markdown(
                    '<div class="empty-chat-state">'
                    '<div class="empty-chat-title">AI Venture Advisor</div>'
                    '<div class="empty-chat-subtitle">Ask me anything about your validation report.</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown("<div class='empty-chat-prompt-label'>Suggested questions</div>", unsafe_allow_html=True)

                suggested_questions = [
                    ("What is the biggest risk?", "advisor_sq_risk"),
                    ("What is my viability score?", "advisor_sq_score"),
                    ("How can I improve my GTM strategy?", "advisor_sq_gtm"),
                    ("Who are my main competitors?", "advisor_sq_comp"),
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
                        st.markdown(
                            '<div class="chat-msg user-msg">'
                            '<div class="msg-author">You</div>'
                            f'<div class="msg-content">{content}</div>'
                            '</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<div class="chat-msg assistant-msg">'
                            '<div class="msg-author">AI Venture Advisor</div>'
                            '<div class="msg-content">',
                            unsafe_allow_html=True
                        )
                        st.markdown(content)
                        st.markdown("</div></div>", unsafe_allow_html=True)

                # Context-aware follow-up question suggestions
                if st.session_state.chat_history and current_state and current_state.final_report:
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
                            ("How can I reduce this risk?", "advisor_fu_1"),
                            ("Which risk should I address first?", "advisor_fu_2"),
                        ],
                        "competition": [
                            ("How can we differentiate?", "advisor_fu_1"),
                            ("What should our competitive moat be?", "advisor_fu_2"),
                        ],
                        "market": [
                            ("How can we validate market demand?", "advisor_fu_1"),
                            ("Which segment should we target first?", "advisor_fu_2"),
                        ],
                        "mvp": [
                            ("What features belong in V1?", "advisor_fu_1"),
                            ("How can we reduce MVP development cost?", "advisor_fu_2"),
                        ],
                        "gtm": [
                            ("Which channel should we test first?", "advisor_fu_1"),
                            ("How can we reduce CAC?", "advisor_fu_2"),
                        ],
                        "funding": [
                            ("What would investors question?", "advisor_fu_1"),
                            ("How can we improve readiness?", "advisor_fu_2"),
                        ],
                        "score": [
                            ("What would increase the score?", "advisor_fu_1"),
                            ("Which dimension is weakest?", "advisor_fu_2"),
                        ],
                        "general": [
                            ("What should I do next?", "advisor_fu_1"),
                            ("What is the biggest opportunity?", "advisor_fu_2"),
                        ],
                    }

                    followups = followup_map.get(detected_intent, followup_map["general"])

                    st.markdown("<div class='followup-divider'></div>", unsafe_allow_html=True)
                    st.caption("**Suggested follow-up questions**")
                    for fu_text, fu_key in followups:
                        with st.container(key=fu_key):
                            if st.button(fu_text, key=f"btn_{fu_key}_{len(st.session_state.chat_history)}"):
                                handle_question_submit(fu_text)

        # -----------------------------------------------------
        # E. PINNED CHAT COMPOSER AT BOTTOM
        # -----------------------------------------------------
        st.markdown("<div class='composer-container'>", unsafe_allow_html=True)
        with st.form(key="advisor_input_form", clear_on_submit=True):
            col_in, col_btn = st.columns([5.2, 1.2], vertical_alignment="center")
            with col_in:
                user_question = st.text_input(
                    "Advisor Question",
                    placeholder="Ask about your market, competitors, risks...",
                    key="advisor_question_input",
                    label_visibility="collapsed",
                )
            with col_btn:
                submitted = st.form_submit_button("Send", help="Send question")

        if submitted and user_question.strip():
            handle_question_submit(user_question.strip())
        st.markdown("</div>", unsafe_allow_html=True)