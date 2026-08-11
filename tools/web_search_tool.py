import os
from dotenv import load_dotenv
from state.schema import WebSearchResults, SearchResultItem
from tools.tavily_tool import TavilySearchTool

load_dotenv()


class WebSearchTool:
    def __init__(self, api_key: str = None):
        self.tavily = TavilySearchTool(api_key=api_key)

    def _convert(self, results):
        items = []
        for r in results:
            items.append(
                SearchResultItem(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("snippet", "") or r.get("content", "")
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
        items = self._convert(raw_results)

        return WebSearchResults(
            market_trends=items,
            competitors=items,
            customer_pain_points=items,
            industry_news=items,
            funding=items,
        )

    def search(self, query: str):
        return self.run_multi_query_search(query)