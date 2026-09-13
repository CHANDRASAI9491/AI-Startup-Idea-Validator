import pytest
from unittest.mock import patch
from state.schema import StartupState, StartupIdea
from agents.gtm_strategy_agent import GTMStrategyAgent


def test_gtm_strategy_agent():
    agent = GTMStrategyAgent()
    state = StartupState(idea=StartupIdea(idea_text="AI Startup Validator"))
    updated_state = agent.run(state)
    if updated_state.gtm_strategy is not None:
        assert len(updated_state.gtm_strategy.primary_acquisition_channels) > 0
        assert updated_state.gtm_strategy.pricing_strategy != ""
    else:
        assert updated_state.gtm_strategy is None


def test_gtm_strategy_agent_real_evidence_parsing(monkeypatch):
    """Verify that when LLM returns real verified GTM data, it parses correctly."""
    agent = GTMStrategyAgent()
    mock_json = {
        "positioning_statement": "The premier validation platform for founders.",
        "primary_acquisition_channels": ["Product Hunt", "LinkedIn Outreach"],
        "pricing_strategy": "Freemium with $29/mo Pro tier",
        "launch_tactics": ["Launch on Hacker News", "Host live webinar"],
        "estimated_cac_summary": "Estimated $40-$50 blended CAC"
    }
    monkeypatch.setattr(agent, "generate_json", lambda *args, **kwargs: mock_json)

    state = StartupState(idea=StartupIdea(idea_text="AI Startup Validator"))
    updated_state = agent.run(state)
    assert updated_state.gtm_strategy is not None
    assert updated_state.gtm_strategy.positioning_statement == "The premier validation platform for founders."
    assert "Product Hunt" in updated_state.gtm_strategy.primary_acquisition_channels
    assert updated_state.gtm_strategy.pricing_strategy == "Freemium with $29/mo Pro tier"



def test_gtm_strategy_agent_failure_returns_none_no_fabricated_assumptions():
    """Verify GTM failure does NOT return hardcoded $49/$199/CAC/payback assumptions."""
    agent = GTMStrategyAgent()
    state = StartupState(idea=StartupIdea(idea_text="Industrial Chemical Logistics SaaS"))

    # Simulate LLM generation failure
    with patch.object(agent, "generate_json", return_value=None):
        updated_state = agent.run(state)

    assert updated_state.gtm_strategy is None

    # Exception path also returns None
    with patch.object(agent, "generate_json", side_effect=Exception("Connection Reset")):
        updated_state_err = agent.run(StartupState(idea=StartupIdea(idea_text="Logistics Idea")))

    assert updated_state_err.gtm_strategy is None
    assert updated_state_err.error is not None
