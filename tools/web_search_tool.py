import logging
from typing import List, Dict, Any, Optional
from state.schema import SearchResultItem, WebSearchResults
from services.search_service import SearchService
from services.logger import get_logger

logger = get_logger(__name__)


class WebSearchTool:
    """Search Tool wrapper utilizing Tavily Search API and SearchService deduplication/ranking."""

    def __init__(self, api_key: Optional[str] = None):
        self.search_service = SearchService(api_key=api_key)

    def search_market_data(self, query: str, max_results: int = 5) -> List[SearchResultItem]:
        return self.search_service.search_topic(query, category="market", max_results=max_results)

    def run_multi_query_search(self, idea_text: str, industry: str = "Technology", max_results: int = 3) -> WebSearchResults:
        """Executes multi-category Tavily queries across trends, competitors, pain points, news, and funding."""
        return self.search_service.execute_multi_category_search(
            idea_text=idea_text,
            industry=industry,
            max_results=max_results
        )
