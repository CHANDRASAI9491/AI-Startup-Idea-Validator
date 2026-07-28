import os
import json
from typing import Dict, Any, Optional, List
from state.schema import AgentState


class MemoryStore:
    """In-memory and file-backed storage for agent states and past validation reports."""

    def __init__(self, storage_dir: str = ".validation_memory"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self._memory_cache: Dict[str, AgentState] = {}

    def save_state(self, session_id: str, state: AgentState) -> None:
        self._memory_cache[session_id] = state
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))

    def get_state(self, session_id: str) -> Optional[AgentState]:
        if session_id in self._memory_cache:
            return self._memory_cache[session_id]
        
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                state = AgentState.model_validate(data)
                self._memory_cache[session_id] = state
                return state
        return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        sessions = []
        if not os.path.exists(self.storage_dir):
            return sessions

        for fname in os.listdir(self.storage_dir):
            if fname.endswith(".json"):
                session_id = fname[:-5]
                state = self.get_state(session_id)
                if state:
                    sessions.append({
                        "session_id": session_id,
                        "idea": state.idea.idea_text,
                        "status": state.status,
                        "score": state.final_report.overall_viability_score if state.final_report else None,
                        "verdict": state.final_report.verdict if state.final_report else None,
                        "timestamp": state.final_report.timestamp if state.final_report else None
                    })
        return sorted(sessions, key=lambda x: x.get("timestamp") or "", reverse=True)
