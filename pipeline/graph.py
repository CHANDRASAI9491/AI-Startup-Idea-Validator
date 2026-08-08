import logging
from typing import Callable, Optional
from state.schema import StartupState, StartupIdea
from pipeline.deep_agents_orchestrator import StartupValidatorDeepAgentsPipeline
from services.logger import get_logger

logger = get_logger(__name__)



class ValidationGraph:
    """Validation Orchestrator wrapped with the official Deep Agents Framework Pipeline."""

    def __init__(self):
        self.pipeline = StartupValidatorDeepAgentsPipeline()

    def run(self, idea: StartupIdea, progress_callback: Optional[Callable[[str, str], None]] = None) -> StartupState:
        return self.pipeline.run(idea, progress_callback=progress_callback)

