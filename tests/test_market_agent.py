import pytest
from state.schema import StartupState, StartupIdea, WebSearchResults, SearchResultItem, MarketAnalysis
from agents.market_analysis_agent import MarketAnalysisAgent


def test_market_analysis_agent_no_evidence_fallback():
    """Verify that when evidence is unavailable, MarketAnalysisAgent returns honest unavailable values."""
    agent = MarketAnalysisAgent()
    state = StartupState(
        idea=StartupIdea(idea_text="AI Fitness Planner", target_industry="Health"),
        search_results=WebSearchResults()
    )
    updated_state = agent.run(state)
    assert updated_state.market_analysis is not None
    assert updated_state.market_analysis.tam_billions is None
    assert updated_state.market_analysis.sam_billions is None
    assert updated_state.market_analysis.som_billions is None
    assert updated_state.market_analysis.cagr_percentage is None
    assert updated_state.market_analysis.market_readiness_score is None
    assert "could not be established" in updated_state.market_analysis.market_size_summary
    # Ensure it never fabricates the old hardcoded $15.0B TAM
    assert updated_state.market_analysis.tam_billions != 15.0


def test_market_analysis_agent_real_evidence_parsing(monkeypatch):
    """Verify that when LLM returns real verified market analysis, it parses correctly."""
    agent = MarketAnalysisAgent()
    mock_json = {
        "tam_billions": 22.5,
        "sam_billions": 5.0,
        "som_billions": 0.8,
        "market_size_summary": "Verified market report indicates $22.5B market size.",
        "cagr_percentage": 16.2,
        "key_growth_drivers": ["Enterprise adoption"],
        "target_personas": [],
        "market_readiness_score": 82
    }
    monkeypatch.setattr(agent, "generate_json", lambda *args, **kwargs: mock_json)

    state = StartupState(
        idea=StartupIdea(idea_text="AI Fitness Planner", target_industry="Health"),
        search_results=WebSearchResults(
            market_trends=[SearchResultItem(title="Market Research", url="https://valid-domain.com/report", snippet="TAM is $22.5B")]
        )
    )
    updated_state = agent.run(state)
    assert updated_state.market_analysis is not None
    assert updated_state.market_analysis.tam_billions == 22.5
    assert updated_state.market_analysis.cagr_percentage == 16.2
    assert updated_state.market_analysis.market_readiness_score == 82
