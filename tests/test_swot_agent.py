import pytest
from state.schema import StartupState, StartupIdea, WebSearchResults
from agents.swot_risk_agent import SWOTRiskAgent


def test_swot_risk_agent():
    agent = SWOTRiskAgent()
    state = StartupState(
        idea=StartupIdea(idea_text="AI Fitness Planner", target_industry="Health"),
        search_results=WebSearchResults()
    )
    updated_state = agent.run(state)
    assert updated_state.swot_analysis is not None
    assert len(updated_state.swot_analysis.strengths) > 0
    assert 0 <= updated_state.swot_analysis.overall_risk_score <= 10
