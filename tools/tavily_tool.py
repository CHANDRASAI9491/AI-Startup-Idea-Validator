import logging
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from app.config import config
from tools.retrieval_utils import RetrievalUtils, SearchResultItem

logger = logging.getLogger(__name__)


class TavilySearchTool:
    """Tavily Search Tool wrapper with Tavily Python SDK / REST API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.TAVILY_API_KEY

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        results = []

        if self.api_key:
            # 1. Attempt Tavily Python SDK
            try:
                from tavily import TavilyClient  # type: ignore
                client = TavilyClient(api_key=self.api_key)
                response = client.search(query=query, max_results=max_results)
                for item in response.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", "") or item.get("snippet", "")
                    })
            except Exception as e_sdk:
                logger.debug(f"Tavily SDK attempt exception, falling back to Tavily REST API: {e_sdk}")

                # 2. Attempt Tavily REST API
                try:
                    url = "https://api.tavily.com/search"
                    payload = json.dumps({
                        "api_key": self.api_key,
                        "query": query,
                        "max_results": max_results,
                        "search_depth": "basic"
                    }).encode("utf-8")

                    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        for item in data.get("results", []):
                            results.append({
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "snippet": item.get("content", "") or item.get("snippet", "")
                            })
                except Exception as e_api:
                    logger.warning(f"Tavily REST API search error for query '{query}': {e_api}")

        if not results:
            logger.info(f"No Tavily evidence returned for query '{query}'")
            return []

        return results

    def perform_validation_search(
        self,
        idea_text: str,
        industry: Optional[str] = "",
        max_results: int = 3
    ) -> Any:
        """Execute structured multi-category web search across trends, competitors, and pain points."""
        from services.search_service import SearchService
        search_svc = SearchService(api_key=self.api_key)
        return search_svc.execute_multi_category_search(
            idea_text=idea_text,
            industry=industry or "",
            max_results=max_results
        )


from langchain_core.tools import tool  # type: ignore


@tool
def tavily_search_tool(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search the web for market trends, competitors, customer pain points, and industry news using Tavily Search API.
    
    Args:
        query: Search query string.
        max_results: Maximum number of search results to return (default: 5).
    """
    search_tool = TavilySearchTool()
    return search_tool.search(query=query, max_results=max_results)

