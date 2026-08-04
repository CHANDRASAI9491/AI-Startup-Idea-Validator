import logging
from typing import Optional, Dict, Any
from state.schema import StartupState
from services.llm_service import LLMService
from services.prompt_loader import PromptLoader
from services.logger import get_logger
from app.config import config

logger = get_logger(__name__)


class BaseAgent:
    """Abstract Base Class for all specialized AI validation agents in Clean Architecture layout."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or config.DEFAULT_MODEL
        self.llm_service = LLMService(model_name=self.model_name)

    def load_prompt(self, prompt_name: str, **kwargs: Any) -> str:
        """Loads prompt template dynamically via PromptLoader service."""
        return PromptLoader.load_prompt(prompt_name, **kwargs)

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        return self.llm_service.generate_text(prompt, system_instruction)

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return self.llm_service.generate_json(prompt, system_instruction)

    def execute(self, state: StartupState) -> StartupState:
        """Abstract execution method to be overridden by subclasses."""
        raise NotImplementedError("Derived agent must implement execute(state) or run(state)")

    def run(self, state: StartupState) -> StartupState:
        """Standard execution entrypoint for graph and unit tests."""
        return self.execute(state)
