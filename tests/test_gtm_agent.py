import pytest
from state.schema import StartupState, StartupIdea
from agents.gtm_strategy_agent import GTMStrategyAgent


def test_gtm_strategy_agent():
    agent = GTMStrategyAgent()
    state = StartupState(idea=StartupIdea(idea_text="AI Startup Validator"))
    updated_state = agent.run(state)
    assert updated_state.gtm_strategy is not None
    assert len(updated_state.gtm_strategy.primary_acquisition_channels) > 0
    assert updated_state.gtm_strategy.pricing_strategy != ""
