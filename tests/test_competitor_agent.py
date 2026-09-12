import pytest
from state.schema import StartupState, StartupIdea, WebSearchResults, SearchResultItem, CompetitorAnalysis, CompetitorItem
from agents.competitor_agent import CompetitorAgent


def test_competitor_agent_no_evidence_fallback():
    """Verify that when evidence is unavailable, CompetitorAgent returns empty lists and no fake URLs."""
    agent = CompetitorAgent()
    state = StartupState(
        idea=StartupIdea(idea_text="AI Fitness Planner", target_industry="Health"),
        search_results=WebSearchResults()
    )
    updated_state = agent.run(state)
    assert updated_state.competitor_analysis is not None
    assert len(updated_state.competitor_analysis.direct_competitors) == 0
    assert len(updated_state.competitor_analysis.indirect_competitors) == 0
    assert "No verified competitors" in updated_state.competitor_analysis.market_positioning_summary
    # Ensure no example.com or example.org or Incumbent Core SaaS
    all_names = [c.name for c in updated_state.competitor_analysis.direct_competitors + updated_state.competitor_analysis.indirect_competitors]
    all_urls = [c.url for c in updated_state.competitor_analysis.direct_competitors + updated_state.competitor_analysis.indirect_competitors]
    assert "Incumbent Core SaaS" not in all_names
    assert not any("example.com" in u or "example.org" in u for u in all_urls)


def test_competitor_agent_real_evidence_parsing(monkeypatch):
    """Verify that when LLM returns real verified competitor data, it parses correctly."""
    agent = CompetitorAgent()
    mock_json = {
        "direct_competitors": [
            {
                "name": "MyFitnessPal",
                "url": "https://www.myfitnesspal.com",
                "description": "Popular fitness tracking and calorie counting app",
                "key_features": ["Calorie database", "Barcode scanner"],
                "pricing_model": "Freemium ($19.99/mo Premium)",
                "strengths": ["Massive brand recognition"],
                "weaknesses": ["Manual food logging fatigue"]
            }
        ],
        "indirect_competitors": [],
        "feature_comparison_matrix": {"AI Workout Generation": {"Us": "Yes", "MyFitnessPal": "No"}},
        "market_positioning_summary": "AI-first automated workout planner competing with legacy manual logging.",
        "moat_assessment": "Proprietary generative workout algorithms and dynamic telemetry loops."
    }
    monkeypatch.setattr(agent, "generate_json", lambda *args, **kwargs: mock_json)

    state = StartupState(
        idea=StartupIdea(idea_text="AI Fitness Planner", target_industry="Health"),
        search_results=WebSearchResults(
            competitors=[SearchResultItem(title="MyFitnessPal", url="https://www.myfitnesspal.com", snippet="Popular app")]
        )
    )
    updated_state = agent.run(state)
    assert updated_state.competitor_analysis is not None
    assert len(updated_state.competitor_analysis.direct_competitors) == 1
    assert updated_state.competitor_analysis.direct_competitors[0].name == "MyFitnessPal"
    assert updated_state.competitor_analysis.direct_competitors[0].url == "https://www.myfitnesspal.com"
