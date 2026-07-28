import pytest
from state.schema import StartupIdea
from agents.mvp_recommendation_agent import MVPRecommendationAgent


def test_mvp_recommendation_agent():
    agent = MVPRecommendationAgent()
    idea = StartupIdea(idea_text="AI Fitness Planner")
    result = agent.run(idea)
    assert result is not None
    assert result.core_value_proposition != ""
    assert len(result.features) > 0
    assert len(result.four_week_roadmap) > 0
