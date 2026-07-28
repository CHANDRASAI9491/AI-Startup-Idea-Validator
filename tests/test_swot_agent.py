import pytest
from state.schema import StartupIdea, WebSearchResults
from agents.swot_risk_agent import SWOTRiskAgent


def test_swot_risk_agent():
    agent = SWOTRiskAgent()
    idea = StartupIdea(idea_text="AI Fitness Planner", target_industry="Health")
    search_results = WebSearchResults()
    result = agent.run(idea, search_results)
    assert result is not None
    assert len(result.strengths) > 0
    assert 0 <= result.overall_risk_score <= 10
