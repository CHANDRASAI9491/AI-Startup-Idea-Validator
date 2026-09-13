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


# ============================================================================
# PHASE 2A: Targeted Evidence Provenance & Source Metadata Tests
# ============================================================================

from datetime import datetime
from state.schema import SearchResultItem, WebSearchResults
from services.search_service import SearchService
from tools.retrieval_utils import format_search_results_summary


def test_search_result_item_metadata_fields():
    """1. SearchResultItem metadata: verify all metadata fields exist."""
    item = SearchResultItem(
        title="AI Medical Diagnostics",
        url="https://medai-research.org/study",
        snippet="Clinical diagnosis using transformer models.",
        query="AI healthcare diagnosis",
        category="Market Trends",
        retrieved_at="2026-09-12T14:00:00+00:00"
    )
    assert item.title == "AI Medical Diagnostics"
    assert item.url == "https://medai-research.org/study"
    assert item.snippet == "Clinical diagnosis using transformer models."
    assert item.query == "AI healthcare diagnosis"
    assert item.category == "Market Trends"
    assert item.retrieved_at == "2026-09-12T14:00:00+00:00"


def test_query_preservation():
    """2. Query preservation: SearchService attaches query to SearchResultItem."""
    service = SearchService(api_key="mock-key")
    with patch.object(service.tavily_tool, "search") as mock_search:
        mock_search.return_value = [
            {"title": "Test Title", "url": "https://example.com/test", "snippet": "A test snippet longer than 20 characters."}
        ]
        items = service.search_topic("quantum computing cloud", category="Market Trends")
        assert len(items) == 1
        assert items[0].query == "quantum computing cloud"


def test_category_preservation():
    """3. Category preservation: SearchService attaches category to SearchResultItem."""
    service = SearchService(api_key="mock-key")
    with patch.object(service.tavily_tool, "search") as mock_search:
        mock_search.return_value = [
            {"title": "Competitor Title", "url": "https://comp.org/product", "snippet": "Competitor snippet longer than 20 characters."}
        ]
        items = service.search_topic("competitor landscape query", category="Competitors")
        assert len(items) == 1
        assert items[0].category == "Competitors"


def test_valid_retrieval_timestamp_for_new_results():
    """4. Valid retrieval timestamp for NEW results: actual ISO timestamp set at retrieval."""
    service = SearchService(api_key="mock-key")
    with patch.object(service.tavily_tool, "search") as mock_search:
        mock_search.return_value = [
            {"title": "News Title", "url": "https://technews.com/ai", "snippet": "Recent artificial intelligence breakthroughs."}
        ]
        items = service.search_topic("ai innovation news", category="Industry News")

        assert len(items) == 1
        ts_str = items[0].retrieved_at
        assert ts_str != "" and ts_str is not None
        # Parse ISO timestamp to ensure valid formatting
        parsed_ts = datetime.fromisoformat(ts_str)
        assert parsed_ts is not None


def test_search_service_preserves_metadata():
    """5. SearchService preserves metadata in execute_multi_category_search."""
    service = SearchService(api_key="mock-key")
    with patch.object(service.tavily_tool, "search") as mock_search:
        mock_search.return_value = [
            {"title": "Market Sizing Report", "url": "https://marketdata.org/sizing", "snippet": "Market size estimate exceeding 20 characters."}
        ]
        results = service.execute_multi_category_search("Autonomous drone logistics", industry="SupplyChain")

        assert len(results.market_trends) == 1
        assert results.market_trends[0].category == "Market Trends"
        assert "Autonomous drone logistics" in results.market_trends[0].query
        assert results.market_trends[0].retrieved_at != ""
        assert results.competitors[0].category == "Competitors"
        assert results.customer_pain_points[0].category == "Customer Pain Points"


def test_missing_url_not_replaced_by_tavily_com():
    """6. Missing URL is not replaced by https://tavily.com and is excluded."""
    service = SearchService(api_key="mock-key")
    with patch.object(service.tavily_tool, "search") as mock_search:
        # One item with empty URL, one with default tavily.com URL, one with valid URL
        mock_search.return_value = [
            {"title": "Bad 1", "url": "", "snippet": "Snippet without URL that is long enough."},
            {"title": "Bad 2", "url": "https://tavily.com", "snippet": "Snippet with generic tavily domain."},
            {"title": "Valid", "url": "https://legit-source.org/report", "snippet": "Valid snippet with a real URL."}
        ]
        items = service.search_topic("test query")
        assert len(items) == 1
        assert items[0].title == "Valid"
        assert items[0].url == "https://legit-source.org/report"


def test_retrieval_summaries_contain_real_urls():
    """7. Retrieval summaries contain real URLs for agent visibility."""
    results = WebSearchResults(
        market_trends=[
            SearchResultItem(
                title="Global SaaS Sizing",
                url="https://saas-data.com/report-2026",
                snippet="SaaS sector CAGR 18.2%."
            )
        ],
        competitors=[
            SearchResultItem(
                title="Incumbent Enterprise Tool",
                url="https://incumbent-soft.com",
                snippet="Leading legacy platform."
            )
        ]
    )
    summary = format_search_results_summary(results)
    assert "https://saas-data.com/report-2026" in summary
    assert "https://incumbent-soft.com" in summary
    assert "(Source: https://saas-data.com/report-2026)" in summary


def test_empty_search_results_remain_safe():
    """8. Empty search results return safe Insufficient evidence indicator."""
    empty_results = WebSearchResults()
    summary = format_search_results_summary(empty_results)
    assert "Insufficient evidence / No live research available." in summary

    summary_none = format_search_results_summary(None)
    assert "Insufficient evidence / No live research available." in summary_none


def test_backward_compatibility_three_args():
    """9. Existing callers that create SearchResultItem with only title/url/snippet remain compatible."""
    item = SearchResultItem(
        title="Legacy Format Item",
        url="https://legacy-domain.org",
        snippet="Snippet with minimum arguments."
    )
    assert item.title == "Legacy Format Item"
    assert item.url == "https://legacy-domain.org"
    assert item.snippet == "Snippet with minimum arguments."
    assert item.query == ""
    assert item.category == ""
    assert item.retrieved_at == ""


def test_existing_history_compatibility_no_fake_timestamp():
    """10. Existing reports/history remain compatible without assigning fake current timestamps."""
    historical_raw_data = {
        "title": "Historical Validated Concept",
        "url": "https://historical-archive.org/doc",
        "snippet": "Archive data stored from a previous validation run."
    }
    deserialized = SearchResultItem.model_validate(historical_raw_data)
    assert deserialized.title == "Historical Validated Concept"
    assert deserialized.url == "https://historical-archive.org/doc"
    # Crucial: Must NOT have assigned a new current timestamp!
    assert deserialized.retrieved_at == ""
    assert deserialized.query == ""
    assert deserialized.category == ""