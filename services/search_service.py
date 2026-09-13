import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from state.schema import SearchResultItem, WebSearchResults
from tools.tavily_tool import TavilySearchTool
from tools.retrieval_utils import RetrievalUtils
from services.logger import get_logger

logger = get_logger(__name__)


class SearchService:
    """Unified Search Service utilizing Tavily Search API with deduplication, ranking, evidence extraction, and citation tracking."""

    def __init__(self, api_key: Optional[str] = None):
        self.tavily_tool = TavilySearchTool(api_key=api_key)

    def search_topic(self, query: str, category: str = "general", max_results: int = 5) -> List[SearchResultItem]:
        """Performs search on a topic, deduplicates, and ranks by relevance."""
        logger.info(f"SearchService executing query [{category}]: '{query}'")
        raw_results = self.tavily_tool.search(query, max_results=max_results)
        
        retrieval_time = datetime.now(timezone.utc).isoformat()
        items = []
        for r in raw_results:
            raw_url = str(r.get("url", "")).strip()
            # Do NOT use https://tavily.com as fallback default.
            # Results without a valid real URL should not be treated as sourced evidence.
            if not raw_url or raw_url.lower() in ["https://tavily.com", "http://tavily.com", "none"]:
                continue
            items.append(
                SearchResultItem(
                    title=r.get("title", "Market Insight"),
                    url=raw_url,
                    snippet=r.get("snippet", ""),
                    query=query,
                    category=category,
                    retrieved_at=retrieval_time
                )
            )

        # Deduplicate by URL and length
        unique_items = RetrievalUtils.deduplicate_results(items)

        # Rank snippets based on query terms
        query_keywords = [w for w in query.split() if len(w) > 3]
        ranked_items = RetrievalUtils.rank_snippets(unique_items, query_keywords)

        return ranked_items

    def execute_multi_category_search(
        self,
        idea_text: str,
        industry: str = "Technology",
        max_results: int = 3
    ) -> WebSearchResults:
        """Executes multi-query Tavily searches across market trends, competitors, customer pain points, news, and funding."""
        base_query = f"{idea_text[:70]} {industry}".strip()

        market_trends = self.search_topic(f"{base_query} market size trends growth CAGR", category="Market Trends", max_results=max_results)
        competitors = self.search_topic(f"{base_query} top competitors alternatives market landscape", category="Competitors", max_results=max_results)
        pain_points = self.search_topic(f"{base_query} customer pain points complaints demand", category="Customer Pain Points", max_results=max_results)
        industry_news = self.search_topic(f"{base_query} industry news tech innovation", category="Industry News", max_results=max_results)
        funding = self.search_topic(f"{base_query} startup funding venture capital investments", category="Funding Intel", max_results=max_results)

        return WebSearchResults(
            market_trends=market_trends,
            competitors=competitors,
            customer_pain_points=pain_points,
            industry_news=industry_news,
            funding=funding
        )

