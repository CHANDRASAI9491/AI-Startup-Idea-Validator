import streamlit as st
from state.schema import StartupState
from app.orchestrator import ApplicationOrchestrator


def render_advisor_chat(orchestrator: ApplicationOrchestrator, state: StartupState):
    """Renders enterprise AI Startup Advisor chat interface without emojis."""
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="saas-section-title">Interactive AI Startup Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="saas-subtitle">Ask follow-up questions regarding your market size, pricing model, competitor moats, or MVP technical architecture grounded in your completed validation report.</div>', unsafe_allow_html=True)

    if not state or not state.final_report:
        st.info("Please complete a startup validation on the main page prior to asking questions.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    idea = state.idea
    st.markdown(f"**Concept Description:** {idea.idea_text}")
    st.markdown(f"**Industry Sector:** {idea.target_industry} | **Business Model:** {idea.business_model}")
    st.markdown("<hr style='margin: 12px 0 16px 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    # Render Conversation History
    for msg in st.session_state.chat_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            st.markdown(f'<div class="chat-bubble-user"><strong>Founder:</strong> {content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-assistant"><strong>AI Advisor:</strong> {content}</div>', unsafe_allow_html=True)

    # User Question Input Bar
    user_q = st.chat_input("Ask a follow-up question regarding your validation analysis...")
    if user_q:
        st.session_state.chat_history.append({"role": "user", "content": user_q})

        with st.spinner("Advisor analyzing validation context..."):
            session_id = st.session_state.session_id or "default"
            answer = orchestrator.ask_advisor(session_id, user_q, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
