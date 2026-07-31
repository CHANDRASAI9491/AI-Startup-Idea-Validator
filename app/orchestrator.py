import uuid
import os
import logging
from typing import Callable, Optional, Dict, Any, List
from state.schema import StartupIdea, StartupState
from state.memory import MemoryStore
from pipeline.graph import ValidationGraph
from tools.file_tools import FileTools
from agents.conversational_advisor import ConversationalAdvisor
from app.config import config

logger = logging.getLogger(__name__)


class ApplicationOrchestrator:
    """Application Orchestrator managing memory, LangGraph execution, report exports, and advisor."""

    def __init__(self):
        self.memory = MemoryStore()
        self.graph = ValidationGraph()
        self.advisor = ConversationalAdvisor()

    def validate_idea(
        self,
        idea_text: str,
        target_industry: str = "Technology / SaaS",
        target_audience: str = "General Users / Businesses",
        business_model: str = "B2B SaaS / Subscription",
        budget: str = "Bootstrap ($5k - $50k)",
        timeline: str = "3 Months",
        session_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str, str], None]] = None
    ) -> StartupState:
        session_id = session_id or str(uuid.uuid4())[:8]

        idea = StartupIdea(
            idea_text=idea_text,
            target_industry=target_industry,
            target_audience=target_audience,
            business_model=business_model,
            budget=budget,
            timeline=timeline
        )

        state = self.graph.run(idea, progress_callback=progress_callback)
        self.memory.save_state(session_id, state)

        # Automatically export report files to output directory
        if state.final_report:
            out_dir = config.REPORTS_DIR
            md_path = os.path.join(out_dir, f"report_{session_id}.md")
            json_path = os.path.join(out_dir, f"report_{session_id}.json")
            pdf_path = os.path.join(out_dir, f"report_{session_id}.pdf")
            
            FileTools.export_report_markdown(state, md_path)
            FileTools.export_report_json(state, json_path)
            FileTools.export_report_pdf(state, pdf_path)

        return state

    def ask_advisor(self, session_id: str, user_question: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        state = self.memory.get_state(session_id)
        if not state:
            return f"Session '{session_id}' not found. Please run a validation first."
        return self.advisor.answer_question(user_question, state, chat_history or [])

    def get_session_history(self, session_id: str) -> Optional[StartupState]:
        return self.memory.get_state(session_id)

    def list_all_sessions(self) -> List[Dict[str, Any]]:
        return self.memory.list_sessions()
