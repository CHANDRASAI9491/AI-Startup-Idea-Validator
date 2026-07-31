import logging
from agents.base_agent import BaseAgent
from tools.web_search_tool import WebSearchTool
from state.schema import StartupState
from app.config import config

logger = logging.getLogger(__name__)


class WebSearchAgent(BaseAgent):
    """Web Search Agent using WebSearchTool to populate state.search_results."""

    def __init__(self, model_name: str = None):
        super().__init__(model_name=model_name)
        self.search_tool = WebSearchTool()

    def run(self, state: StartupState) -> StartupState:
        logger.info(f"WebSearchAgent running for idea: {state.idea.idea_text}")
        try:
            results = self.search_tool.run_multi_query_search(
                state.idea.idea_text,
                max_results=config.MAX_SEARCH_RESULTS
            )
            state.search_results = results
        except Exception as e:
            logger.error(f"Error in WebSearchAgent: {e}")
            state.error = f"WebSearchAgent error: {str(e)}"
        return state