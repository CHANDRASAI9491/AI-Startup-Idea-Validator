import os
from tavily import TavilyClient
from dotenv import load_dotenv

from state.schema import WebSearchResults, SearchResultItem

load_dotenv()


class WebSearchTool:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in .env")

        self.client = TavilyClient(api_key=api_key)

    def _convert(self, results):

        items = []

        for r in results:
            items.append(
                SearchResultItem(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", "")
                )
            )

        return items

    def run_multi_query_search(
        self,
        query: str,
        industry: str = "",
        max_results: int = 5,
    ) -> WebSearchResults:

        if industry:
            query = f"{query} {industry}"

        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
        )

        items = self._convert(response.get("results", []))

        return WebSearchResults(
            market_trends=items,
            competitors=items,
            customer_pain_points=items,
            industry_news=items,
            funding=items,
        )

    def search(self, query: str):
        return self.run_multi_query_search(query)