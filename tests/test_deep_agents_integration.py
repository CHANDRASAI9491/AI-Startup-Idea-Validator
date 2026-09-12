import pytest
import json
from langchain_core.messages import AIMessage, HumanMessage
from deepagents import create_deep_agent, SubAgent, DeepAgentState
from state.schema import StartupIdea, StartupState, MarketAnalysis
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


def test_deep_agent_result_is_consumed_to_populate_state():
    """Verify that deep_result returned by deep_agent.invoke() is mapped into StartupState."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="AI-driven Supply Chain Optimizer", target_industry="Logistics")

    fake_custom_payload = {
        "market_analysis": {
            "tam_billions": 42.5,
            "sam_billions": 10.0,
            "som_billions": 1.2,
            "market_size_summary": "Custom TAM $42.5B extracted from deep_result",
            "cagr_percentage": 22.0,
            "key_growth_drivers": ["Supply chain automation"],
            "target_personas": [],
            "market_readiness_score": 90
        }
    }

    fake_deep_result = {
        "messages": [
            HumanMessage(content="Validate idea"),
            AIMessage(content=json.dumps(fake_custom_payload))
        ],
        "structured_response": fake_custom_payload,
        "files": {}
    }

    state = StartupState(idea=idea)

    def dummy_notify(s, st):
        pass

    pipeline._map_deep_result_to_state(state, fake_deep_result, dummy_notify)

    # Prove that the custom deep_result value is mapped into state
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 42.5
    assert state.market_analysis.sam_billions == 10.0
    assert state.market_analysis.cagr_percentage == 22.0
    assert "Custom TAM $42.5B" in state.market_analysis.market_size_summary


def test_fails_if_deep_agent_result_is_ignored():
    """Test that fails if deep_result custom data is ignored in favor of hardcoded defaults."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Quantum AI Encryption Key Manager", target_industry="Cybersecurity")

    custom_tam = 999.9
    fake_deep_result = {
        "structured_response": {
            "market_analysis": {
                "tam_billions": custom_tam,
                "sam_billions": 200.0,
                "som_billions": 20.0,
                "market_size_summary": "Quantum TAM $999.9B",
                "cagr_percentage": 35.0,
                "key_growth_drivers": ["Quantum resistance"],
                "target_personas": [],
                "market_readiness_score": 95
            }
        }
    }

    state = StartupState(idea=idea)
    pipeline._map_deep_result_to_state(state, fake_deep_result, lambda s, st: None)

    # Must equal custom_tam (999.9), NOT static default 15.0 or 10.0
    assert state.market_analysis.tam_billions == 999.9
    assert state.market_analysis.tam_billions != 15.0


def test_orchestrator_honest_fallback_no_fabricated_data():
    """Verify that orchestrator fallback does not calculate text-length TAM or invent competitors."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    # Provide an idea with specific length to prove text_factor is no longer applied
    idea = StartupIdea(
        idea_text="Short idea",
        target_industry="FinTech"
    )
    state = StartupState(idea=idea)
    pipeline._map_deep_result_to_state(state, None, lambda s, st: None)

    # Market analysis must be None, not 12.0 + text_factor
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions is None
    assert state.market_analysis.sam_billions is None
    assert state.market_analysis.cagr_percentage is None
    assert "could not be established" in state.market_analysis.market_size_summary

    # Competitor analysis must be empty, not Primary FinTech Competitor with example.com
    assert state.competitor_analysis is not None
    assert len(state.competitor_analysis.direct_competitors) == 0
    assert len(state.competitor_analysis.indirect_competitors) == 0
    assert "No verified competitors" in state.competitor_analysis.market_positioning_summary
    all_urls = [c.url for c in state.competitor_analysis.direct_competitors + state.competitor_analysis.indirect_competitors]
    assert not any("example.com" in u or "example.org" in u for u in all_urls)

    # Report takeaways must not claim a fabricated TAM
    assert state.final_report is not None
    assert any("could not be established" in t for t in state.final_report.key_takeaways)
    assert not any("$None" in t for t in state.final_report.key_takeaways)


def test_report_generation_with_missing_evidence(tmp_path):
    """Verify that Markdown and PDF file export does not print fake numbers when evidence is None."""
    from tools.file_tools import FileTools
    from state.schema import MarketAnalysis, CompetitorAnalysis, ValidationReport
    from services.scoring_engine import DeterministicScoringEngine

    idea = StartupIdea(idea_text="AI BioTech Drug Discovery", target_industry="BioTech")
    market = MarketAnalysis(tam_billions=None, cagr_percentage=None)
    comp = CompetitorAnalysis(
        direct_competitors=[],
        market_positioning_summary="No verified competitors identified from available research."
    )
    scoring = DeterministicScoringEngine.calculate_scores(
        idea_text=idea.idea_text,
        target_industry=idea.target_industry,
        tam_billions=None,
        cagr_percentage=None,
        direct_competitor_count=None
    )
    report = ValidationReport(
        overall_viability_score=scoring.total_viability_score,
        verdict=scoring.verdict,
        executive_summary="Summary",
        scoring_breakdown=scoring
    )
    state = StartupState(idea=idea, market_analysis=market, competitor_analysis=comp, final_report=report)

    md_file = str(tmp_path / "test_report.md")
    FileTools.export_report_markdown(state, md_file)
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    assert "Evidence unavailable" in md_content
    assert "No verified competitors identified" in md_content
    assert "$None" not in md_content
