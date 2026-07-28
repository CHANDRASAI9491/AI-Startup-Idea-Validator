import pytest
from state.schema import StartupIdea, WebSearchResults, SearchResultItem
from agents.competitor_agent import CompetitorAgent


def test_competitor_agent():
    agent = CompetitorAgent()
    idea = StartupIdea(idea_text="AI Fitness Planner", target_industry="Health")
    search_results = WebSearchResults(
        competitors=[SearchResultItem(title="MyFitnessPal", url="http://mfp.com", snippet="Popular app")]
    )
    result = agent.run(idea, search_results)
    assert result is not None
    assert len(result.direct_competitors) > 0
    assert result.moat_assessment != ""
