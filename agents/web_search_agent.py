import logging
from agents.base_agent import BaseAgent
from tools.web_search_tool import WebSearchTool
from state.schema import StartupState
from app.config import config
from services.logger import get_logger

logger = get_logger(__name__)


class WebSearchAgent(BaseAgent):
    """Web Search Agent using Tavily WebSearchTool to gather evidence across market trends, competitors, and pain points."""

    def __init__(self, model_name: str = None):
        super().__init__(model_name=model_name)
        self.search_tool = WebSearchTool()

    def execute(self, state: StartupState) -> StartupState:
        logger.info(f"WebSearchAgent collecting research snippets for concept: '{state.idea.idea_text}'")
        try:
            results = self.search_tool.run_multi_query_search(
                idea_text=state.idea.idea_text,
                industry=state.idea.target_industry or "Technology",
                max_results=config.MAX_SEARCH_RESULTS
            )
            state.search_results = results
        except Exception as e:
            logger.error(f"Error in WebSearchAgent: {e}")
            state.error = f"WebSearchAgent error: {str(e)}"
        return state