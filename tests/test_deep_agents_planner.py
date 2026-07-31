import pytest
from tools.planning_tool import DeepAgentsPlanner
from state.schema import StartupIdea, DeepAgentsPlan


def test_deep_agents_planner():
    planner = DeepAgentsPlanner()
    idea = StartupIdea(
        idea_text="AI-powered automated legal contract review tool",
        target_industry="LegalTech",
        target_audience="Corporate Legal Teams"
    )
    plan = planner.plan_validation(idea)
    assert plan is not None
    assert isinstance(plan, DeepAgentsPlan)
    assert len(plan.strategic_objective) > 10
    assert len(plan.research_questions) > 0
    assert "WebSearchAgent" in plan.agent_allocations
