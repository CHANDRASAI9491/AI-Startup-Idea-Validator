import pytest
from deepagents import create_deep_agent, SubAgent
from pipeline.deep_agents_orchestrator import StartupValidatorDeepAgentsPipeline
from tools.tavily_tool import tavily_search_tool


def test_deep_agents_subagent_registration():
    """Verify that all six subagents are registered on StartupValidatorDeepAgentsPipeline."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    assert pipeline.subagents is not None
    assert len(pipeline.subagents) == 6

    registered_names = [sub["name"] for sub in pipeline.subagents]
    expected_subagents = [
        "market-research",
        "competitor-research",
        "swot-risk",
        "mvp",
        "gtm",
        "report"
    ]

    for expected in expected_subagents:
        assert expected in registered_names, f"Expected subagent '{expected}' not found in registered subagents."


def test_deep_agents_subagent_tool_binding():
    """Verify tool assignment for market-research and competitor-research subagents."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    subagent_map = {sub["name"]: sub for sub in pipeline.subagents}

    # Verify market-research has tavily_search_tool
    market_sub = subagent_map.get("market-research")
    assert market_sub is not None
    assert "tools" in market_sub
    assert len(market_sub["tools"]) > 0
    assert tavily_search_tool in market_sub["tools"]

    # Verify competitor-research has tavily_search_tool
    competitor_sub = subagent_map.get("competitor-research")
    assert competitor_sub is not None
    assert "tools" in competitor_sub
    assert len(competitor_sub["tools"]) > 0
    assert tavily_search_tool in competitor_sub["tools"]


def test_deep_agent_instance_creation():
    """Verify compiled Deep Agent graph instance creation."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    assert pipeline.deep_agent is not None
    assert hasattr(pipeline.deep_agent, "invoke")
