import pytest
from tools.tavily_tool import TavilySearchTool
from tools.web_search_tool import WebSearchTool


def test_tavily_search_tool():
    tool = TavilySearchTool()
    results = tool.search("AI Startup Validator market trends", max_results=3)
    assert results is not None
    assert len(results) > 0
    assert "title" in results[0]
    assert "url" in results[0]
    assert "snippet" in results[0]


def test_web_search_tool_tavily():
    search_tool = WebSearchTool()
    multi_results = search_tool.run_multi_query_search("AI healthcare platform", industry="HealthTech", max_results=2)
    assert multi_results is not None
    assert len(multi_results.market_trends) > 0