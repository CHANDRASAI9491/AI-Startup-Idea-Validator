import os
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


def get_tavily_client():
    """Initializes and returns a TavilyClient using TAVILY_API_KEY environment variable."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY environment variable is not configured.")
        return None
    try:
        from tavily import TavilyClient
        return TavilyClient(api_key=api_key)
    except Exception as e:
        logger.warning(f"Failed to initialize TavilyClient: {e}")
        return None


def tavily_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Performs a Tavily web search using the configured TAVILY_API_KEY."""
    client = get_tavily_client()
    if not client:
        return []
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        return response.get("results", []) if isinstance(response, dict) else []
    except Exception as e:
        logger.warning(f"Tavily search exception for query '{query}': {e}")
        return []