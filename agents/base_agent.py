import logging
from typing import Optional, Dict, Any
from state.schema import StartupState
from services.llm_service import LLMService
from app.config import config

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all AI validation agents in Clean Architecture layout."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or config.DEFAULT_MODEL
        self.llm_service = LLMService(model_name=self.model_name)

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        return self.llm_service.generate_text(prompt, system_instruction)

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return self.llm_service.generate_json(prompt, system_instruction)

    def execute(self, state: StartupState) -> StartupState:
        """Abstract execution method."""
        raise NotImplementedError("Derived agent must implement execute(state) or run(state)")

    def run(self, state: StartupState) -> StartupState:
        """Standard execution entrypoint for graph and unit tests."""
        return self.execute(state)
