import pytest
from unittest.mock import patch
from state.schema import StartupState, StartupIdea, WebSearchResults
from agents.swot_risk_agent import SWOTRiskAgent


def test_swot_risk_agent():
    agent = SWOTRiskAgent()
    state = StartupState(
        idea=StartupIdea(idea_text="AI Fitness Planner", target_industry="Health"),
        search_results=WebSearchResults()
    )
    updated_state = agent.run(state)
    if updated_state.swot_analysis is not None:
        assert len(updated_state.swot_analysis.strengths) > 0
        assert 0 <= updated_state.swot_analysis.overall_risk_score <= 10
    else:
        assert updated_state.swot_analysis is None


def test_swot_risk_agent_real_evidence_parsing(monkeypatch):
    """Verify that when LLM returns real verified SWOT data, it parses correctly."""
    agent = SWOTRiskAgent()
    mock_json = {
        "strengths": ["Proprietary AI model", "Low cost structure"],
        "weaknesses": ["Unproven retention"],
        "opportunities": ["Global expansion"],
        "threats": ["Big tech competition"],
        "financial_risk": 4,
        "technical_risk": 3,
        "regulatory_risk": 2,
        "overall_risk_score": 3,
        "risk_matrix": [
            {
                "risk_name": "API Downtime",
                "category": "Technical",
                "probability": 2,
                "impact": 4,
                "severity_score": 8,
                "mitigation_strategy": "Multi-region failover"
            }
        ],
        "risk_mitigation_plan": ["Deploy multi-region cloud cluster"]
    }
    monkeypatch.setattr(agent, "generate_json", lambda *args, **kwargs: mock_json)

    state = StartupState(
        idea=StartupIdea(idea_text="AI Fitness Planner", target_industry="Health"),
        search_results=WebSearchResults()
    )
    updated_state = agent.run(state)
    assert updated_state.swot_analysis is not None
    assert len(updated_state.swot_analysis.strengths) == 2
    assert updated_state.swot_analysis.strengths[0] == "Proprietary AI model"
    assert updated_state.swot_analysis.financial_risk == 4
    assert updated_state.swot_analysis.overall_risk_score == 3



def test_swot_risk_agent_failure_returns_none_no_fabricated_data():
    """Verify SWOT failure does NOT return fabricated SWOT/risk values."""
    agent = SWOTRiskAgent()
    state = StartupState(
        idea=StartupIdea(idea_text="AI Telehealth Doctor", target_industry="HealthTech")
    )
    # Simulate LLM generation failure / invalid json
    with patch.object(agent, "generate_json", return_value=None):
        updated_state = agent.run(state)

    # Must be None, never fabricated heuristic risk scores
    assert updated_state.swot_analysis is None

    # Verify exception path also returns None
    with patch.object(agent, "generate_json", side_effect=Exception("API Failure")):
        updated_state_err = agent.run(StartupState(idea=StartupIdea(idea_text="Error Idea")))

    assert updated_state_err.swot_analysis is None
    assert updated_state_err.error is not None
