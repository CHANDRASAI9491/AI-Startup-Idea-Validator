import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from state.schema import WebSearchResults, SearchResultItem
from tools.tavily_tool import TavilySearchTool

load_dotenv()


class WebSearchTool:
    def __init__(self, api_key: str = None):
        self.tavily = TavilySearchTool(api_key=api_key)

    def _convert(self, results, query: str = "", category: str = ""):
        items = []
        retrieval_time = datetime.now(timezone.utc).isoformat()
        for r in results:
            raw_url = str(r.get("url", "")).strip()
            if not raw_url or raw_url.lower() in ["https://tavily.com", "http://tavily.com", "none"]:
                continue
            items.append(
                SearchResultItem(
                    title=r.get("title", ""),
                    url=raw_url,
                    snippet=r.get("snippet", "") or r.get("content", ""),
                    query=query,
                    category=category,
                    retrieved_at=retrieval_time
                )
            )
        return items

    def run_multi_query_search(
        self,
        query: str,
        industry: str = "",
        max_results: int = 5,
    ) -> WebSearchResults:
        full_query = f"{query} {industry}".strip() if industry else query
        raw_results = self.tavily.search(query=full_query, max_results=max_results)

        return WebSearchResults(
            market_trends=self._convert(raw_results, query=full_query, category="Market Trends"),
            competitors=self._convert(raw_results, query=full_query, category="Competitors"),
            customer_pain_points=self._convert(raw_results, query=full_query, category="Customer Pain Points"),
            industry_news=self._convert(raw_results, query=full_query, category="Industry News"),
            funding=self._convert(raw_results, query=full_query, category="Funding Intel"),
        )

    def search(self, query: str):
        return self.run_multi_query_search(query)
