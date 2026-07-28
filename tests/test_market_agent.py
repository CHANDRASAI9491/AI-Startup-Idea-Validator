import pytest
from state.schema import StartupIdea, WebSearchResults, SearchResultItem
from agents.market_analysis_agent import MarketAnalysisAgent


def test_market_analysis_agent():
    agent = MarketAnalysisAgent()
    idea = StartupIdea(idea_text="AI Fitness Planner", target_industry="Health")
    search_results = WebSearchResults(
        market_trends=[SearchResultItem(title="Fitness Trends", url="http://ex.com", snippet="Growing market")]
    )
    result = agent.run(idea, search_results)
    assert result is not None
    assert result.tam_billions > 0
    assert result.market_readiness_score >= 0
    assert len(result.key_growth_drivers) > 0
