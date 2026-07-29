import pytest
from tools.duckduckgo_tool import DuckDuckGoTool


def test_duckduckgo_search():
    tool = DuckDuckGoTool()
    results = tool.search("AI Startup Validator market trends", max_results=3)
    assert results is not None
    assert len(results) > 0
    assert "title" in results[0]
    assert "url" in results[0]
    assert "snippet" in results[0]