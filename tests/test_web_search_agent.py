import pytest
from agents.web_search_agent import WebSearchAgent
from state.schema import StartupState, StartupIdea


def test_web_search_agent():
    agent = WebSearchAgent()
    state = StartupState(idea=StartupIdea(idea_text="AI Startup Validator", target_industry="Technology"))
    
    updated_state = agent.run(state)
    
    assert updated_state.search_results is not None
    assert hasattr(updated_state.search_results, "market_trends")
    assert isinstance(updated_state.search_results.market_trends, list)