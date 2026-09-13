import pytest
from unittest.mock import patch
from state.schema import StartupState, StartupIdea
from agents.mvp_recommendation_agent import MVPRecommendationAgent


def test_mvp_recommendation_agent():
    agent = MVPRecommendationAgent()
    state = StartupState(idea=StartupIdea(idea_text="AI Fitness Planner"))
    updated_state = agent.run(state)
    if updated_state.mvp_recommendation is not None:
        assert updated_state.mvp_recommendation.core_value_proposition != ""
        assert len(updated_state.mvp_recommendation.features) > 0
        assert len(updated_state.mvp_recommendation.four_week_roadmap) > 0
    else:
        assert updated_state.mvp_recommendation is None


def test_mvp_recommendation_agent_real_evidence_parsing(monkeypatch):
    """Verify that when LLM returns real verified MVP data, it parses correctly."""
    agent = MVPRecommendationAgent()
    mock_json = {
        "core_value_proposition": "Custom workout plans generated dynamically",
        "features": [
            {
                "feature_name": "Workout Generator",
                "description": "Generates workout routine",
                "priority": "Must Have",
                "estimated_days": 5
            }
        ],
        "target_timeline_weeks": 4,
        "tech_stack_frontend": "Next.js",
        "tech_stack_backend": "FastAPI",
        "tech_stack_database": "PostgreSQL",
        "tech_stack_ai": "Gemini 2.5 Flash",
        "four_week_roadmap": {"Week 1": "Core logic", "Week 2": "UI integration"},
        "key_metrics_kpis": ["Daily Active Users", "Plan completion rate"]
    }
    monkeypatch.setattr(agent, "generate_json", lambda *args, **kwargs: mock_json)

    state = StartupState(idea=StartupIdea(idea_text="AI Fitness Planner"))
    updated_state = agent.run(state)
    assert updated_state.mvp_recommendation is not None
    assert updated_state.mvp_recommendation.core_value_proposition == "Custom workout plans generated dynamically"
    assert updated_state.mvp_recommendation.tech_stack_frontend == "Next.js"
    assert len(updated_state.mvp_recommendation.features) == 1



def test_mvp_recommendation_agent_failure_returns_none_no_validator_architecture():
    """Verify MVP failure does NOT return the validator application's own architecture."""
    agent = MVPRecommendationAgent()
    state = StartupState(idea=StartupIdea(idea_text="Autonomous Farming Drone"))

    # Simulate LLM generation failure
    with patch.object(agent, "generate_json", return_value=None):
        updated_state = agent.run(state)

    assert updated_state.mvp_recommendation is None

    # Exception path also returns None
    with patch.object(agent, "generate_json", side_effect=Exception("LLM Timeout")):
        updated_state_err = agent.run(StartupState(idea=StartupIdea(idea_text="Drone Idea")))

    assert updated_state_err.mvp_recommendation is None
    assert updated_state_err.error is not None
