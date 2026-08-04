import logging
from typing import List, Dict, Any
from tools.tavily_tool import TavilySearchTool
from services.logger import get_logger

logger = get_logger(__name__)


class DuckDuckGoTool:
    """Deprecated DuckDuckGo search wrapper refactored to delegate directly to Tavily Search Engine."""

    def __init__(self):
        self.tavily_tool = TavilySearchTool()

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"DuckDuckGoTool redirecting search query to Tavily Search Engine: '{query}'")
        return self.tavily_tool.search(query, max_results=max_results)