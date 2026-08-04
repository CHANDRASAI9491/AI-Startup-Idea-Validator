import streamlit as st
from typing import List, Dict, Any, Optional
from state.schema import StartupState
from app.orchestrator import ApplicationOrchestrator


def render_advisor_chat(orchestrator: ApplicationOrchestrator, state: Optional[StartupState]) -> None:
    """Renders the Grounded AI Venture Advisor Q&A Chatbot Interface."""
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="saas-card-header"><div class="saas-title">Grounded AI Venture Advisor</div></div>', unsafe_allow_html=True)

    if not state or not state.final_report:
        st.info("No active validation report found. Please validate a startup concept on the main page to enable AI Advisor Q&A.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.markdown(f"Consult with your AI Strategic Advisor regarding **'{state.idea.idea_text}'**. Answers are grounded strictly in your generated validation report.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-advisor"><b>AI Advisor:</b> {content}</div>', unsafe_allow_html=True)

    # Question Input
    user_q = st.text_input("Ask a follow-up question about your validation report:", key="advisor_question_input", placeholder="e.g. What is the biggest risk? How can I lower initial CAC?")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Send Question"):
            if user_q.strip():
                st.session_state.chat_history.append({"role": "user", "content": user_q})
                
                with st.spinner("AI Advisor analyzing report data..."):
                    answer = orchestrator.ask_advisor(
                        session_id=st.session_state.get("session_id", "default"),
                        user_question=user_q,
                        chat_history=st.session_state.chat_history
                    )
                
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

    with col2:
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
