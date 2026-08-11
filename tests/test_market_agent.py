import pytest
from state.schema import StartupState, StartupIdea, WebSearchResults, SearchResultItem
from agents.market_analysis_agent import MarketAnalysisAgent


def test_market_analysis_agent():
    agent = MarketAnalysisAgent()
    state = StartupState(
        idea=StartupIdea(idea_text="AI Fitness Planner", target_industry="Health"),
        search_results=WebSearchResults(
            market_trends=[SearchResultItem(title="Fitness Trends", url="http://ex.com", snippet="Growing market")]
        )
    )
    updated_state = agent.run(state)
    assert updated_state.market_analysis is not None
    assert updated_state.market_analysis.tam_billions > 0
    assert 0 <= updated_state.market_analysis.market_readiness_score <= 100
    assert len(updated_state.market_analysis.key_growth_drivers) > 0
