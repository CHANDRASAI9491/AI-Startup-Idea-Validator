import os
import re
import html
import base64
from urllib.parse import urlparse
import streamlit as st
from typing import Optional, List, Dict, Any, Tuple

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


def _parse_advisor_sources(text: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Parses the advisor response text to cleanly separate markdown body
    and structured sources if '### Additional Web Research' or '### Sources' is present.
    """
    sources_pattern = r"(?:###\s+(?:Additional Web Research|Sources|Web Sources))\s*\n([\s\S]*)"
    match = re.search(sources_pattern, text, re.IGNORECASE)
    
    if not match:
        return text, []

    main_text = text[:match.start()].strip()
    sources_block = match.group(1).strip()
    
    sources = []
    line_pattern = r"[-*]?\s*(?:\[(.*?)\])?(?:\s*[\(—\-:]\s*|\s+)?(https?://[^\s\)]+)"
    for line in sources_block.split("\n"):
        line = line.strip()
        if not line:
            continue
        line_match = re.search(line_pattern, line)
        if line_match:
            title = line_match.group(1) or ""
            url = line_match.group(2).rstrip(".)")
            domain = urlparse(url).netloc.replace("www.", "")
            if not title:
                title = domain
            sources.append({
                "title": title.strip(" []"),
                "url": url.strip(),
                "domain": domain
            })

    return main_text, sources


def render_advisor_chat(
    orchestrator: ApplicationOrchestrator,
    state: Optional[StartupState],
) -> None:
    """Render the Grounded AI Venture Advisor floating popup with top-left history button, + New Chat, and pill-styled suggested questions."""

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
    active_conv_id = st.session_state.get("active_conversation_id")

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
    # 2. FLOATING CIRCULAR LAUNCHER BUTTON (BOTTOM-RIGHT)
    # ---------------------------------------------------------
    st.markdown(
        '<div id="ai-advisor-launcher-anchor"></div>',
        unsafe_allow_html=True
    )

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

        spinner_text = "Researching current market information..." if needs_web else "Thinking..."

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
    # 4. FLOATING CHATBOT WINDOW CONTAINER
    # ---------------------------------------------------------
    with st.container(key="floating_advisor_panel"):

        # -----------------------------------------------------
        # 1. HEADER BAR: History Icon -> AI Venture Advisor -> Status -> Close
        # -----------------------------------------------------
        has_report = bool(current_state and current_state.final_report)
        status_class = "active" if has_report else "inactive"
        status_text = "Report active" if has_report else "No active report"

        icon_img_html = f"<img src='{SVG_ICON_DATA_URI}' class='header-bot-icon' alt='Advisor' />" if SVG_ICON_DATA_URI else ""

        col_hist, col_hdr, col_close = st.columns([1.1, 6.2, 1.1], vertical_alignment="center")

        with col_hist:
            # Top-Left History Icon Button with Dropdown List of Conversations
            with st.popover("🕒", help="Chat History & Saved Conversations"):
                st.markdown("<div class='history-popover-title'>Saved Conversations</div>", unsafe_allow_html=True)
                history_list = list_conversations()
                if not history_list:
                    st.markdown("<p style='font-size: 11px; color: #64748B; padding: 4px 0;'>No saved conversations found.</p>", unsafe_allow_html=True)
                else:
                    curr_id = st.session_state.get("active_conversation_id")
                    for c in history_list:
                        cid = c["id"]
                        title = c.get("title", "Conversation")
                        if len(title) > 28:
                            title = title[:25] + "..."
                        
                        c_item, c_del = st.columns([4.2, 1.2], vertical_alignment="center")
                        with c_item:
                            is_active = (cid == curr_id)
                            prefix = "▶ " if is_active else ""
                            if st.button(f"{prefix}{title}", key=f"pop_conv_{cid}", use_container_width=True):
                                st.session_state.active_conversation_id = cid
                                st.session_state.chat_history = [
                                    {"role": m["role"], "content": m["content"]}
                                    for m in get_messages(cid)
                                ]
                                st.rerun()
                        with c_del:
                            if st.button("🗑", key=f"pop_del_{cid}", help="Delete this chat"):
                                delete_conversation(cid)
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

        with col_hdr:
            hdr_html = (
                '<div class="advisor-header-brand">'
                f'{icon_img_html}'
                '<div>'
                '<div class="advisor-header-title">AI Venture Advisor</div>'
                f'<div class="advisor-header-status {status_class}">'
                f'<span class="status-indicator-dot"></span>{status_text}'
                '</div>'
                '</div>'
                '</div>'
            )
            st.markdown(hdr_html, unsafe_allow_html=True)

        with col_close:
            if st.button("✕", key="advisor_close", help="Close Advisor"):
                st.session_state.advisor_open = False
                st.rerun()

        st.markdown("<div class='advisor-header-divider'></div>", unsafe_allow_html=True)

        # -----------------------------------------------------
        # 2. SUB-HEADER BAR: CHAT HISTORY / + New Chat
        # -----------------------------------------------------
        col_sub_lbl, col_sub_new = st.columns([5.2, 2.8], vertical_alignment="center")

        with col_sub_lbl:
            active_cid = st.session_state.get("active_conversation_id")
            active_meta = get_conversation(active_cid) if active_cid else None
            active_title = active_meta.get("title", "New Conversation") if active_meta else "New Conversation"
            if len(active_title) > 28:
                active_title = active_title[:25] + "..."
            st.markdown(
                f'<div class="chat-history-sub-header">'
                f'<span class="history-label-tag">CHAT HISTORY</span>'
                f'<span class="history-active-title">• {html.escape(active_title)}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        with col_sub_new:
            if st.button("+ New Chat", key="advisor_new_chat", help="Start new fresh conversation"):
                new_id = create_conversation(
                    title="New Conversation",
                    session_id=st.session_state.get("session_id")
                )
                st.session_state.active_conversation_id = new_id
                st.session_state.chat_history = []
                st.rerun()

        st.markdown("<div class='chat-history-divider'></div>", unsafe_allow_html=True)

        # -----------------------------------------------------
        # 3. MAIN CONTENT VIEW (WELCOME SCREEN VS CONVERSATION THREAD)
        # -----------------------------------------------------
        if not st.session_state.chat_history:
            # -------------------------------------------------
            # WELCOME SCREEN VIEW
            # -------------------------------------------------
            with st.container(key="advisor_welcome_view"):
                # AI Venture Advisor welcome message
                welcome_header_html = (
                    '<div class="welcome-hero-container">'
                    f'<div class="welcome-avatar-wrapper">{icon_img_html}</div>'
                    '<h2 class="welcome-title">Hi there! I’m AI Venture Advisor 👋</h2>'
                    '<p class="welcome-subtitle">Ask me anything about your startup.</p>'
                    '</div>'
                )
                st.markdown(welcome_header_html, unsafe_allow_html=True)

                # TRY ASKING Label
                st.markdown('<div class="try-asking-label">TRY ASKING</div>', unsafe_allow_html=True)

                # My 6 suggested questions (2-column layout)
                c1, c2 = st.columns(2)

                col1_questions = [
                    ("What is my biggest risk?", "🛡️ What is my biggest risk?", "advisor_sq_risk"),
                    ("What is my market opportunity?", "📊 What is my market opportunity?", "advisor_sq_market"),
                    ("How can I improve my GTM?", "🚀 How can I improve my GTM?", "advisor_sq_gtm"),
                ]

                col2_questions = [
                    ("Who are my main competitors?", "⚔️ Who are my main competitors?", "advisor_sq_comp"),
                    ("How can I improve my MVP?", "🛠️ How can I improve my MVP?", "advisor_sq_mvp"),
                    ("What is my viability score?", "📈 What is my viability score?", "advisor_sq_score"),
                ]

                with c1:
                    for raw_text, display_text, sq_key in col1_questions:
                        with st.container(key=sq_key):
                            if st.button(display_text, key=f"btn_{sq_key}"):
                                handle_question_submit(raw_text)

                with c2:
                    for raw_text, display_text, sq_key in col2_questions:
                        with st.container(key=sq_key):
                            if st.button(display_text, key=f"btn_{sq_key}"):
                                handle_question_submit(raw_text)

                # Context Badge / No active report warning
                if current_state and current_state.final_report:
                    concept_text = current_state.idea.idea_text or "Current startup concept"
                    if len(concept_text) > 42:
                        concept_text = concept_text[:40] + "..."
                    st.markdown(
                        f'<div class="welcome-context-badge">'
                        f'<span class="context-badge-icon">💡</span>'
                        f'<span>Consulting on: <strong>{html.escape(concept_text)}</strong></span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="welcome-context-badge warning">'
                        '<span class="context-badge-icon">⚠️</span>'
                        '<span><strong>No active report.</strong> Validate an idea first to enable due diligence Q&A.</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )

        else:
            # -------------------------------------------------
            # ACTIVE CONVERSATION THREAD VIEW
            # -------------------------------------------------
            with st.container(height=340, border=False, key="advisor_messages"):
                for msg in st.session_state.chat_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        st.markdown(
                            '<div class="chat-msg user-msg">'
                            '<div class="msg-author">You</div>'
                            f'<div class="msg-content">{html.escape(content)}</div>'
                            '</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        main_body, sources = _parse_advisor_sources(content)
                        
                        st.markdown(
                            '<div class="chat-msg assistant-msg">'
                            '<div class="msg-author">AI Venture Advisor</div>'
                            '<div class="msg-content">',
                            unsafe_allow_html=True
                        )
                        st.markdown(main_body)
                        
                        # Render structured web research sources if present
                        if sources:
                            sources_html = [
                                '<div class="advisor-sources-block">',
                                '<div class="advisor-sources-heading">Sources</div>',
                                '<div class="advisor-sources-grid">'
                            ]
                            for src in sources:
                                title_esc = html.escape(src["title"])
                                url_esc = html.escape(src["url"])
                                domain_esc = html.escape(src["domain"])
                                sources_html.append(
                                    f'<a href="{url_esc}" target="_blank" rel="noopener noreferrer" class="advisor-source-item">'
                                    f'<span class="source-domain">{domain_esc}</span>'
                                    f'<span class="source-title">{title_esc}</span>'
                                    '</a>'
                                )
                            sources_html.append('</div></div>')
                            st.markdown("".join(sources_html), unsafe_allow_html=True)
                        
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
        # 4. BOTTOM INPUT AREA: Ask anything... + mic + send
        # -----------------------------------------------------
        st.markdown("<div class='composer-wrapper'>", unsafe_allow_html=True)
        with st.form(key="advisor_input_form", clear_on_submit=True):
            col_in, col_mic, col_btn = st.columns([5.2, 0.7, 1.1], vertical_alignment="center")
            with col_in:
                user_question = st.text_input(
                    "Advisor Question",
                    placeholder="Ask anything about your startup...",
                    key="advisor_question_input",
                    label_visibility="collapsed",
                )
            with col_mic:
                st.markdown(
                    '<div class="mic-icon-container" title="Voice Input">'
                    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                    '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>'
                    '<path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>'
                    '<line x1="12" y1="19" x2="12" y2="22"></line>'
                    '</svg>'
                    '</div>',
                    unsafe_allow_html=True
                )
            with col_btn:
                submitted = st.form_submit_button("➔", help="Send question")

        if submitted and user_question.strip():
            handle_question_submit(user_question.strip())
        st.markdown("</div>", unsafe_allow_html=True)