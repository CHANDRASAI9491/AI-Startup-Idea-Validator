from unittest.mock import patch, MagicMock
import pytest
from tools.tavily_tool import TavilySearchTool
from tools.web_search_tool import WebSearchTool


def test_tavily_search_real_results():
    """Test 1 - Real results: Mock Tavily so it returns real search results."""
    with patch("tavily.TavilyClient") as mock_client_class:
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.search.return_value = {
            "results": [
                {
                    "title": "Real Market Insights & Trends",
                    "url": "https://realmarketresearch.org/report-2026",
                    "content": "Real-time industry growth data and customer adoption metrics."
                }
            ]
        }

        tool = TavilySearchTool(api_key="mock-api-key")
        results = tool.search("AI Startup Validator market trends", max_results=3)

        assert results is not None
        assert len(results) == 1
        assert results[0]["title"] == "Real Market Insights & Trends"
        assert results[0]["url"] == "https://realmarketresearch.org/report-2026"
        assert results[0]["snippet"] == "Real-time industry growth data and customer adoption metrics."


def test_tavily_search_no_results():
    """Test 2 - Tavily returns no results: returns empty list and no fabricated URLs."""
    with patch("tavily.TavilyClient") as mock_client_class:
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.search.return_value = {"results": []}

        tool = TavilySearchTool(api_key="mock-api-key")
        results = tool.search("rare obscure topic with no web matches", max_results=3)

        assert results == []

        # Verify no fabricated URLs or claims are generated
        fake_markers = ["tavily.com/research", "example.com", "example.org"]
        for res in results:
            url = res.get("url", "")
            for marker in fake_markers:
                assert marker not in url, f"Fabricated URL detected: {url}"


def test_tavily_search_failure():
    """Test 3 - Tavily failure: SDK & REST fail; verify safe empty list without fabricated data."""
    with patch("tavily.TavilyClient") as mock_client_class, \
         patch("urllib.request.urlopen") as mock_urlopen:
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.search.side_effect = Exception("Tavily SDK network timeout")
        mock_urlopen.side_effect = Exception("Tavily REST HTTP connection refused")

        tool = TavilySearchTool(api_key="mock-api-key")
        results = tool.search("AI Startup Validator market trends", max_results=3)

        assert results == []

        fake_markers = ["tavily.com/research", "example.com", "example.org"]
        for res in results:
            url = res.get("url", "")
            for marker in fake_markers:
                assert marker not in url, f"Fabricated URL detected: {url}"


def test_tavily_search_no_api_key():
    """Verify search without API key returns empty list without fabricated data."""
    with patch("tools.tavily_tool.config.TAVILY_API_KEY", None):
        tool = TavilySearchTool(api_key=None)
        results = tool.search("any query", max_results=3)
        assert results == []


def test_web_search_tool_with_results():
    """Verify WebSearchTool handles real results properly."""
    with patch.object(TavilySearchTool, "search") as mock_search:
        mock_search.return_value = [
            {
                "title": "HealthTech AI Analysis",
                "url": "https://healthai-news.com/article",
                "snippet": "Healthcare machine learning tools and diagnostics."
            }
        ]

        search_tool = WebSearchTool(api_key="mock-api-key")
        multi_results = search_tool.run_multi_query_search("AI healthcare platform", industry="HealthTech", max_results=2)

        assert multi_results is not None
        assert len(multi_results.market_trends) == 1
        assert multi_results.market_trends[0].title == "HealthTech AI Analysis"
        assert multi_results.market_trends[0].url == "https://healthai-news.com/article"


def test_web_search_tool_empty_results():
    """Verify WebSearchTool returns empty result lists when Tavily returns no results."""
    with patch.object(TavilySearchTool, "search") as mock_search:
        mock_search.return_value = []

        search_tool = WebSearchTool(api_key="mock-api-key")
        multi_results = search_tool.run_multi_query_search("AI healthcare platform", industry="HealthTech", max_results=2)

        assert multi_results is not None
        assert multi_results.market_trends == []
        assert multi_results.competitors == []
        assert multi_results.customer_pain_points == []
        assert multi_results.industry_news == []
        assert multi_results.funding == []