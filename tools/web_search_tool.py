import logging
from typing import List, Dict, Any
from state.schema import SearchResultItem, WebSearchResults
from tools.duckduckgo_tool import DuckDuckGoTool
from tools.retrieval_utils import RetrievalUtils

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Search Tool wrapper utilizing DuckDuckGo search and RetrievalUtils deduplication."""

    def __init__(self):
        self.search_tool = DuckDuckGoTool()

    def search_market_data(self, query: str, max_results: int = 5) -> List[SearchResultItem]:
        raw_items = self.search_tool.search(query, max_results=max_results)
        items = [SearchResultItem(**item) for item in raw_items]
        return RetrievalUtils.deduplicate_results(items)

    def run_multi_query_search(self, idea_text: str, industry: str = "Technology", max_results: int = 3) -> WebSearchResults:
        """Executes multi-category queries across trends, competitors, pain points, news, and funding."""
        query_base = f"{idea_text[:60]} {industry}"

        trends = self.search_market_data(f"{query_base} market trends growth", max_results=max_results)
        competitors = self.search_market_data(f"{query_base} competitors market landscape", max_results=max_results)
        pain_points = self.search_market_data(f"{query_base} customer pain points demand", max_results=max_results)
        news = self.search_market_data(f"{query_base} industry news technology", max_results=max_results)
        funding = self.search_market_data(f"{query_base} funding startup investment", max_results=max_results)

        return WebSearchResults(
            market_trends=trends,
            competitors=competitors,
            customer_pain_points=pain_points,
            industry_news=news,
            funding=funding
        )
