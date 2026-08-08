import pytest
from deepagents import create_deep_agent, SubAgent, DeepAgentState
from state.schema import StartupIdea, StartupState
from pipeline.deep_agents_orchestrator import StartupValidatorDeepAgentsPipeline
from tools.tavily_tool import tavily_search_tool, TavilySearchTool
from app.orchestrator import ApplicationOrchestrator


def test_deep_agents_import():
    """Verify official deepagents package imports."""
    assert create_deep_agent is not None
    assert SubAgent is not None
    assert DeepAgentState is not None


def test_main_startup_validator_agent_initialization():
    """Verify initialization of Main Startup Validator Agent and subagent specs."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    assert pipeline is not None
    assert pipeline.subagents is not None
    assert len(pipeline.subagents) == 6

    subagent_names = [s["name"] for s in pipeline.subagents]
    expected_names = [
        "market-research",
        "competitor-research",
        "swot-risk",
        "mvp",
        "gtm",
        "report"
    ]
    for name in expected_names:
        assert name in subagent_names, f"Expected subagent '{name}' not found in subagents list."


def test_tavily_search_tool_function():
    """Verify Tavily search tool function for subagents."""
    search_tool = TavilySearchTool()
    results = search_tool.search("AI Healthcare Diagnostic Tool", max_results=2)
    assert results is not None
    assert len(results) > 0
    assert "title" in results[0]
    assert "url" in results[0]


def test_deep_agents_pipeline_execution():
    """Verify end-to-end execution of StartupValidatorDeepAgentsPipeline."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(
        idea_text="AI Platform for Automated Legal Contract Analysis",
        target_industry="LegalTech / AI",
        target_audience="Corporate Law Firms & Legal Teams",
        business_model="B2B SaaS Subscription",
        budget="Bootstrap ($10k)",
        timeline="3 Months"
    )

    steps_recorded = []

    def progress_callback(step, status):
        steps_recorded.append((step, status))

    state = pipeline.run(idea, progress_callback=progress_callback)

    assert state is not None
    assert state.status == "completed"
    assert state.planning_output is not None
    assert state.market_analysis is not None
    assert state.competitor_analysis is not None
    assert state.swot_analysis is not None
    assert state.mvp_recommendation is not None
    assert state.gtm_strategy is not None
    assert state.final_report is not None
    assert 0 <= state.final_report.overall_viability_score <= 100
    assert state.final_report.verdict in ["PROCEED", "PIVOT", "CAUTION", "STOP"]


def test_orchestrator_integration():
    """Verify ApplicationOrchestrator delegates to Deep Agents pipeline."""
    orchestrator = ApplicationOrchestrator()
    state = orchestrator.validate_idea(
        idea_text="Autonomous AI Agent for Code Refactoring",
        target_industry="Developer Tools / AI",
        target_audience="Software Engineering Teams",
        business_model="B2B Subscription",
        budget="$25k",
        timeline="2 Months"
    )
    assert state is not None
    assert state.status == "completed"
    assert state.final_report is not None
