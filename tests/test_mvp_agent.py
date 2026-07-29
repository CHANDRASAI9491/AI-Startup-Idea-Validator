import pytest
from state.schema import StartupState, StartupIdea
from agents.mvp_recommendation_agent import MVPRecommendationAgent


def test_mvp_recommendation_agent():
    agent = MVPRecommendationAgent()
    state = StartupState(idea=StartupIdea(idea_text="AI Fitness Planner"))
    updated_state = agent.run(state)
    assert updated_state.mvp_recommendation is not None
    assert updated_state.mvp_recommendation.core_value_proposition != ""
    assert len(updated_state.mvp_recommendation.features) > 0
    assert len(updated_state.mvp_recommendation.four_week_roadmap) > 0
