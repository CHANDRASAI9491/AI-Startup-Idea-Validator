import pytest
from state.schema import StartupState, StartupIdea, WebSearchResults, SearchResultItem
from agents.competitor_agent import CompetitorAgent


def test_competitor_agent():
    agent = CompetitorAgent()
    state = StartupState(
        idea=StartupIdea(idea_text="AI Fitness Planner", target_industry="Health"),
        search_results=WebSearchResults(
            competitors=[SearchResultItem(title="MyFitnessPal", url="http://mfp.com", snippet="Popular app")]
        )
    )
    updated_state = agent.run(state)
    assert updated_state.competitor_analysis is not None
    assert len(updated_state.competitor_analysis.direct_competitors) > 0
    assert updated_state.competitor_analysis.moat_assessment != ""
