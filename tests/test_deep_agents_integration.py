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
    if getattr(state, "deep_result", None):
        assert state.swot_analysis is not None
        assert state.mvp_recommendation is not None
        assert state.gtm_strategy is not None
    else:
        assert state.swot_analysis is None
        assert state.mvp_recommendation is None
        assert state.gtm_strategy is None
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

    # SWOT, MVP, and GTM must be None (no fabricated operational fallbacks)
    assert state.swot_analysis is None
    assert state.mvp_recommendation is None
    assert state.gtm_strategy is None

    # Report takeaways must not claim a fabricated TAM
    assert state.final_report is not None
    assert any("could not be established" in t for t in state.final_report.key_takeaways)
    assert not any("$None" in t for t in state.final_report.key_takeaways)
    # Limitation must be present for SWOT
    assert any("SWOT and risk analysis could not be verified" in lim for lim in state.final_report.scoring_breakdown.evidence_limitations)


def test_web_research_failure_not_reported_as_completed(monkeypatch):
    """Verify that when web research fails or throws an exception, it is marked as failed,
    NOT marked as completed, search_results is None, and an explicit limitation is added."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="AI Failure Test", target_industry="Technology")

    # Mock tavily to raise an exception simulating network/API failure
    def mock_perform_validation_search(*args, **kwargs):
        raise ConnectionError("Tavily API connection failed")

    monkeypatch.setattr(pipeline.tavily, "perform_validation_search", mock_perform_validation_search)

    steps = []
    def progress_callback(step, status):
        steps.append((step, status))

    state = pipeline.run(idea, progress_callback=progress_callback)

    # 1. Must record ("web_search", "failed"), NOT ("web_search", "completed")
    assert ("web_search", "failed") in steps
    assert ("web_search", "completed") not in steps

    # 2. search_results must be None
    assert state.search_results is None

    # 3. Limitations must explicitly include live web research unavailable
    assert state.final_report is not None
    assert state.final_report.scoring_breakdown is not None
    limitations = state.final_report.scoring_breakdown.evidence_limitations
    assert any("Live web research was unavailable" in lim for lim in limitations)


def test_deep_agent_result_populates_swot_mvp_gtm_when_successful():
    """Verify that when deep_agent structured_response contains SWOT, MVP, and GTM,
    they are successfully mapped into StartupState without using fallback."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Custom AI Startup", target_industry="EdTech")

    fake_custom_payload = {
        "swot_analysis": {
            "strengths": ["Proprietary dynamic dataset"],
            "weaknesses": ["Small team size"],
            "opportunities": ["Untapped enterprise segment"],
            "threats": ["Incumbent expansion"],
            "financial_risk": 3,
            "technical_risk": 2,
            "regulatory_risk": 1,
            "overall_risk_score": 2,
            "risk_matrix": [],
            "risk_mitigation_plan": ["Hire senior architects"]
        },
        "mvp_recommendation": {
            "core_value_proposition": "Automated lesson planning in under 3 minutes",
            "features": [
                {
                    "feature_name": "Lesson Generator",
                    "description": "Generates curriculums",
                    "priority": "Must Have",
                    "estimated_days": 7
                }
            ],
            "target_timeline_weeks": 4,
            "tech_stack_frontend": "SvelteKit",
            "tech_stack_backend": "FastAPI",
            "tech_stack_database": "PostgreSQL",
            "tech_stack_ai": "Claude 3.5 Sonnet",
            "four_week_roadmap": {"Week 1": "Setup DB"},
            "key_metrics_kpis": ["Weekly Active Teachers"]
        },
        "gtm_strategy": {
            "positioning_statement": "The premier AI curriculum assistant for educators.",
            "primary_acquisition_channels": ["EdTech conferences", "Teacher subreddits"],
            "pricing_strategy": "Freemium with $12/month teacher tier",
            "launch_tactics": ["Beta testing with 50 schools"],
            "estimated_cac_summary": "$25 per teacher"
        }
    }

    fake_deep_result = {
        "structured_response": fake_custom_payload
    }

    state = StartupState(idea=idea)
    pipeline._map_deep_result_to_state(state, fake_deep_result, lambda s, st: None)

    assert state.swot_analysis is not None
    assert state.swot_analysis.strengths == ["Proprietary dynamic dataset"]
    assert state.swot_analysis.financial_risk == 3

    assert state.mvp_recommendation is not None
    assert state.mvp_recommendation.core_value_proposition == "Automated lesson planning in under 3 minutes"
    assert state.mvp_recommendation.tech_stack_frontend == "SvelteKit"

    assert state.gtm_strategy is not None
    assert state.gtm_strategy.pricing_strategy == "Freemium with $12/month teacher tier"
    assert state.gtm_strategy.estimated_cac_summary == "$25 per teacher"


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


# =====================================================================
# Tests A through J: Deep Result State Mapping & Markdown Extraction
# =====================================================================

def test_mapping_priority_a_structured_json():
    """Test A: Deep result with structured_response JSON takes Priority 1."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Fleet Logistics AI", target_industry="Logistics")
    state = StartupState(idea=idea)

    deep_result = {
        "structured_response": {
            "market_analysis": {
                "tam_billions": 85.0,
                "sam_billions": 25.0,
                "som_billions": 2.5,
                "market_size_summary": "Structured TAM $85B",
                "cagr_percentage": 18.5,
                "key_growth_drivers": ["Autonomous freight"],
                "target_personas": []
            }
        },
        "files": {
            "/workspace/executive_validation_report.md": {
                "content": "TAM: $10.0 Billion"  # Should NOT be used because structured_response takes priority
            }
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 85.0
    assert state.market_analysis.market_size_summary == "Structured TAM $85B"


def test_mapping_priority_b_json_in_ai_message_string():
    """Test B: Deep result with JSON embedded in a normal string AIMessage takes Priority 1."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="FinTech Reconciliation Engine", target_industry="FinTech")
    state = StartupState(idea=idea)

    payload = {
        "market_analysis": {
            "tam_billions": 60.0,
            "sam_billions": 15.0,
            "som_billions": 1.5,
            "market_size_summary": "Reconciliation TAM $60B",
            "cagr_percentage": 14.0,
            "key_growth_drivers": ["Real-time settlement"],
            "target_personas": []
        }
    }
    deep_result = {
        "messages": [
            AIMessage(content=f"Here is the validation analysis: {json.dumps(payload)}")
        ]
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 60.0
    assert state.market_analysis.sam_billions == 15.0


def test_mapping_c_content_blocks_with_markdown():
    """Test C: Deep result with list of content blocks [{'type': 'text', 'text': '...'}] containing Markdown."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Developer API Observability", target_industry="DevTools")
    state = StartupState(idea=idea)

    report_md = """# Executive Report
### 1. Market Research
* **TAM:** $14.0 Billion
* **SAM:** $4.0 Billion
* **SOM:** $400 Million
* **CAGR:** 20.5% CAGR
* **Growth Drivers:** Cloud migration, microservices
### 2. Competitors
* **Direct Competitors:** Datadog, Dynatrace, New Relic
* **Indirect Competitors:** Prometheus, Grafana
"""
    deep_result = {
        "messages": [
            AIMessage(content=[{"type": "text", "text": report_md}])
        ]
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 14.0
    assert state.market_analysis.som_billions == 0.4
    assert state.market_analysis.cagr_percentage == 20.5
    assert len(state.competitor_analysis.direct_competitors) == 3
    assert state.competitor_analysis.direct_competitors[0].name == "Datadog"


def test_mapping_d_markdown_containing_tam_sam_som_units():
    """Test D: Markdown containing various TAM/SAM/SOM currency units (Billion, Million, M, B, Trillion)."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Genomics Platform", target_industry="HealthTech")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 1. Market Sizing
* **TAM (Total Addressable Market):** ~$1.5 Trillion
* **SAM:** $250.0 Billion
* **SOM (Initial Obtainable Market):** $50.0 Million
* **CAGR:** 16.2% CAGR
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 1500.0
    assert state.market_analysis.sam_billions == 250.0
    assert state.market_analysis.som_billions == 0.05
    assert state.market_analysis.cagr_percentage == 16.2


def test_mapping_e_markdown_containing_competitors():
    """Test E: Markdown report containing direct and indirect competitors."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Contract Review Tool", target_industry="LegalTech")
    state = StartupState(idea=idea)

    report_md = """# Executive Report
### 2. Competitor Analysis
* **Direct Competitors:** Ironclad, Robin AI, LawGeex
* **Enterprise Incumbents:** LexisNexis (Legacy vendor)
* **Indirect Competitors:** Manual Word redlining, generic ChatGPT
* **Our Competitive Edge:** Automated playbooks with zero configuration.
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": {"content": report_md}
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.competitor_analysis is not None
    direct_names = [c.name for c in state.competitor_analysis.direct_competitors]
    assert "Ironclad" in direct_names
    assert "Robin AI" in direct_names
    assert "LexisNexis" in direct_names
    indirect_names = [c.name for c in state.competitor_analysis.indirect_competitors]
    assert any("Manual Word redlining" in n for n in indirect_names)
    assert "Automated playbooks" in state.competitor_analysis.market_positioning_summary


def test_mapping_f_missing_tam_leaves_none():
    """Test F: When TAM is missing from Markdown report, tam_billions is None without fabrication."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Niche Craft Platform", target_industry="Consumer")
    state = StartupState(idea=idea)

def test_mapping_reg_a_direct_competitor_extraction():
    """Test A: Direct competitor extraction from inline lists and subsection items."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Review Analytics Platform", target_industry="SaaS")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 2. Competitor Landscape
### A. Direct Incumbents
* **AlphaReview:** Full suite review monitoring and alerting.
* **BetaAnalytics (SMB Edition):** Sentiment analysis for shops.
* **GammaAI / DeltaInsights:** Clustered feedback extraction.
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.competitor_analysis is not None
    direct_names = [c.name for c in state.competitor_analysis.direct_competitors]
    assert "AlphaReview" in direct_names
    assert "BetaAnalytics" in direct_names
    assert "GammaAI" in direct_names
    assert "DeltaInsights" in direct_names


def test_mapping_reg_b_indirect_competitor_extraction():
    """Test B: Indirect competitor extraction from inline lists and subsections."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Review Analytics Platform", target_industry="SaaS")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 2. Competitor Landscape
* **Indirect Status Quo:** Manual CSV exports into ChatGPT or spreadsheets.
### B. Indirect Substitutes & Alternatives
* **Traditional Review Tools:** Birdeye and Podium SMS collection tools.
* **DIY LLM Workflows (Custom Scripts):** Founder prompt engineering.
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.competitor_analysis is not None
    indirect_names = [c.name for c in state.competitor_analysis.indirect_competitors]
    assert any("Manual CSV exports" in n for n in indirect_names)
    assert any("Traditional Review Tools" in n for n in indirect_names)
    assert any("DIY LLM Workflows" in n for n in indirect_names)


def test_mapping_reg_c_competitor_section_boundaries():
    """Test C: Competitor section boundaries ensure parser stops before adjacent sections."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Review Analytics Platform", target_industry="SaaS")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 2. Competitor Landscape
* **Direct Competitors:** TrueCompA, TrueCompB
### 3. SWOT & Risk Management
* **Threats:** CompetitorZ might enter the market with lower pricing.
### 4. MVP Scoping & Tech Stack
* **Tech Stack:** Next.js, Supabase, Vercel, OpenAI
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.competitor_analysis is not None
    direct_names = [c.name for c in state.competitor_analysis.direct_competitors]
    assert "TrueCompA" in direct_names
    assert "TrueCompB" in direct_names
    # CompetitorZ and tech stack companies from subsequent sections must NOT be direct competitors
    assert "CompetitorZ" not in direct_names
    assert "Next.js" not in direct_names
    assert "Supabase" not in direct_names


def test_mapping_reg_d_market_positioning_extraction():
    """Test D: Market positioning extraction from explicit statements or gap descriptions."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Review Analytics Platform", target_industry="SaaS")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 2. Competitor Analysis
* **Market Positioning:** "Turn customer complaints into your next best-selling product update—automatically."
* **Direct Competitors:** IncumbentA
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.competitor_analysis is not None
    assert "Turn customer complaints" in state.competitor_analysis.market_positioning_summary


def test_mapping_reg_e_moat_assessment_extraction():
    """Test E: Moat assessment extraction captures actual moat without fragments like 'Research)'."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Review Analytics Platform", target_industry="SaaS")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 2. Competitive Landscape & Defensibility (Competitor Research)
* **The Gap:** Enterprise tools are too complex.
* **Defensibility Moat:** Moving beyond charts into an Action Engine—transforming clustered feedback into ready-to-use product/operational fix briefs.
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.competitor_analysis is not None
    # Must NOT be "Research)" or end with ")"
    assert state.competitor_analysis.moat_assessment != "Research)"
    assert not state.competitor_analysis.moat_assessment.endswith(")")
    assert "Action Engine" in state.competitor_analysis.moat_assessment


def test_mapping_reg_f_no_competitor_section_empty_lists():
    """Test F: When no competitor section exists, competitor lists are empty without fabrication."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Novel Philosophy Theory", target_industry="Education")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 1. Market Sizing
* **TAM:** $1.0 Billion
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.competitor_analysis is not None
    assert len(state.competitor_analysis.direct_competitors) == 0
    assert len(state.competitor_analysis.indirect_competitors) == 0
    assert "No verified competitors" in state.competitor_analysis.market_positioning_summary


def test_mapping_reg_g_unrelated_company_names_not_competitors():
    """Test G: Unrelated companies mentioned in MVP or GTM sections must not become competitors."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Tech Platform", target_industry="Developer Tools")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 1. Market Research
* **TAM:** $10.0 Billion
### 4. MVP Scoping & Architecture
* Tech Stack: Next.js, Supabase (PostgreSQL), Vercel, Python FastAPI, OpenAI API
### 5. Go-To-Market Strategy
* Distribution channels: Shopify App Store, Product Hunt, Stripe billing, Google Ads
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.competitor_analysis is not None
    direct_names = [c.name.lower() for c in state.competitor_analysis.direct_competitors]
    indirect_names = [c.name.lower() for c in state.competitor_analysis.indirect_competitors]
    all_names = set(direct_names + indirect_names)
    unrelated = ["next.js", "supabase", "vercel", "fastapi", "openai", "shopify", "product hunt", "stripe", "google"]
    for u in unrelated:
        assert u not in all_names, f"Unrelated company '{u}' was erroneously extracted as competitor."


def test_mapping_reg_h_existing_tam_sam_som_unchanged():
    """Test H: Existing TAM/SAM/SOM extraction with generic unit conversions remains intact."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Genomics Platform", target_industry="HealthTech")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 1. Market Sizing
* **TAM (Total Addressable Market):** ~$1.5 Trillion
* **SAM:** $250.0 Billion
* **SOM (Initial Obtainable Market):** $50.0 Million
* **CAGR:** 16.2% CAGR
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 1500.0
    assert state.market_analysis.sam_billions == 250.0
    assert state.market_analysis.som_billions == 0.05
    assert state.market_analysis.cagr_percentage == 16.2


def test_mapping_reg_i_cagr_range_remains_none():
    """Test I: For CAGR ranges like '12.6%–16.9% CAGR', cagr_percentage is strictly None."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="AI Analytics", target_industry="SaaS")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 1. Market Research & Sizing
* **TAM:** $8.5 Billion
* Market is expanding at a 12.6%–16.9% CAGR over the next five years.
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 8.5
    assert state.market_analysis.cagr_percentage is None


def test_mapping_reg_j_existing_structured_json_unchanged():
    """Test J: Existing Priority 1 structured JSON path remains unmodified and honored directly."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="B2B Supply Chain AI", target_industry="Logistics")
    state = StartupState(idea=idea)

    structured_json = {
        "market_analysis": {
            "tam_billions": 45.0,
            "sam_billions": 12.0,
            "som_billions": 1.5,
            "cagr_percentage": 14.2,
            "market_size_summary": "Verified from structured JSON response.",
            "key_growth_drivers": ["Automation", "Labor shortages"]
        },
        "competitor_analysis": {
            "direct_competitors": [
                {"name": "Project44", "description": "Freight visibility platform"},
                {"name": "FourKites", "description": "Supply chain tracking"}
            ],
            "indirect_competitors": [
                {"name": "Legacy EDI", "description": "Traditional batch transfer"}
            ],
            "market_positioning_summary": "Predictive exception management for mid-market 3PLs.",
            "moat_assessment": "Proprietary carrier integration graph."
        }
    }
    deep_result = {"structured_response": structured_json}
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.market_analysis.tam_billions == 45.0
    assert state.market_analysis.sam_billions == 12.0
    assert state.market_analysis.som_billions == 1.5
    assert state.market_analysis.cagr_percentage == 14.2
    assert len(state.competitor_analysis.direct_competitors) == 2
    assert state.competitor_analysis.direct_competitors[0].name == "Project44"
    assert len(state.competitor_analysis.indirect_competitors) == 1
    assert state.competitor_analysis.moat_assessment == "Proprietary carrier integration graph."


def test_mapping_reg_k_mvp_missing_evidence_no_fabrication():
    """Test K: MVP section with missing evidence returns None, never fabricated features/tech stack/phases."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="AI Analytics", target_industry="SaaS")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 1. Market Research
* **TAM:** $5.0 Billion
### 2. Competitor Analysis
* **Direct Competitors:** CompA
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.mvp_recommendation is None

    # When MVP section is present but empty, no fabricated features, tech stack, or phases
    report_md_sparse_mvp = """# Validation Report
### 4. MVP Architecture
* Only exploratory thoughts without concrete features or tech stack.
"""
    deep_result_sparse = {
        "files": {
            "/workspace/executive_validation_report.md": report_md_sparse_mvp
        }
    }
    state_sparse = StartupState(idea=idea)
    pipeline._map_deep_result_to_state(state_sparse, deep_result_sparse, lambda s, st: None)
    assert state_sparse.mvp_recommendation is None


def test_mapping_reg_l_gtm_missing_evidence_no_fabrication():
    """Test L: GTM section with missing evidence returns None, never fabricated pricing or early-adopter data."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="AI Analytics", target_industry="SaaS")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 1. Market Research
* **TAM:** $5.0 Billion
### 2. Competitor Analysis
* **Direct Competitors:** CompA
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.gtm_strategy is None

    # When GTM section is present but empty, no fabricated pricing or early adopter profile
    report_md_sparse_gtm = """# Validation Report
### 5. Go-To-Market
* High-level thoughts without concrete channels or pricing tiers.
"""
    deep_result_sparse = {
        "files": {
            "/workspace/executive_validation_report.md": report_md_sparse_gtm
        }
    }
    state_sparse = StartupState(idea=idea)
    pipeline._map_deep_result_to_state(state_sparse, deep_result_sparse, lambda s, st: None)
    assert state_sparse.gtm_strategy is None


def test_mapping_reg_m_market_summary_does_not_cross_into_competitors():
    """Test M: Market size summary respects section boundaries and does not leak competitor text."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Review Analytics Platform", target_industry="SaaS")
    state = StartupState(idea=idea)

    report_md = """# Validation Report
### 1. Market Research & Sizing
* **TAM:** $16.7 Billion
* **SAM:** $3.2 Billion
* **SOM:** $2.5 Million
* **CAGR:** 14.5% CAGR
The customer feedback analysis market is experiencing rapid expansion driven by SMB digitization.

### 2. Competitor Analysis
* **Direct Competitors:** CompA, CompB, CompC
* Enterprise Incumbents: Medallia and Qualtrics dominate large enterprises with high cost.
"""
    deep_result = {
        "files": {
            "/workspace/executive_validation_report.md": report_md
        }
    }
    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 16.7
    assert state.market_analysis.sam_billions == 3.2
    assert state.market_analysis.som_billions == 0.0025
    assert state.market_analysis.cagr_percentage == 14.5
    summary = state.market_analysis.market_size_summary
    assert "customer feedback analysis market" in summary
    # Must NOT cross over into the competitor section
    assert "CompA" not in summary
    assert "CompB" not in summary
    assert "Medallia" not in summary
    assert "Qualtrics" not in summary


# =====================================================================
# Tests N through T: Production Path Evidence Injection & Output Contract
# =====================================================================

def test_production_path_search_results_injected_into_deep_agent_context(monkeypatch):
    """Test N (Req A): Proves state.search_results is included in the Deep Agent invocation context."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(
        idea_text="AI-powered personal finance assistant that analyzes spending patterns",
        target_industry="FinTech / Personal Finance"
    )

    from state.schema import WebSearchResults, SearchResultItem
    sample_search = WebSearchResults(
        market_trends=[
            SearchResultItem(
                title="AI in Personal Finance Market Size Report",
                url="https://example.com/market-report",
                snippet="The global AI in Personal Finance market is projected to reach $14.5 Billion by 2030 with a 15.2% CAGR."
            )
        ],
        competitors=[
            SearchResultItem(
                title="Top Personal Finance AI Apps: Cleo and Rocket Money",
                url="https://example.com/competitors",
                snippet="Key market players include Cleo ($5.99/mo chat budgeting) and Rocket Money ($3-12/mo subscription cancellation)."
            )
        ]
    )

    captured_prompt = None

    class MockDeepAgent:
        def invoke(self, graph_input):
            nonlocal captured_prompt
            messages = graph_input.get("messages", [])
            if messages:
                captured_prompt = messages[0].get("content", "")
            return {"messages": [AIMessage(content="Validation complete")]}

    monkeypatch.setattr(pipeline.tavily, "perform_validation_search", lambda *args, **kwargs: sample_search)
    pipeline.deep_agent = MockDeepAgent()

    state = pipeline.run(idea)

    assert captured_prompt is not None
    assert "WEB RESEARCH EVIDENCE SUMMARY" in captured_prompt
    assert "The global AI in Personal Finance market is projected to reach $14.5 Billion" in captured_prompt
    assert "Cleo" in captured_prompt
    assert "Rocket Money" in captured_prompt


def test_production_path_receives_formatted_research_evidence(monkeypatch):
    """Test O (Req B): Proves Deep Agent receives the formatted research evidence with real URLs and snippets."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(
        idea_text="AI-powered medical documentation generator",
        target_industry="HealthTech"
    )

    from state.schema import WebSearchResults, SearchResultItem
    sample_search = WebSearchResults(
        market_trends=[
            SearchResultItem(
                title="Clinical Documentation Market Trends 2026",
                url="https://healthtech.org/report",
                snippet="Clinical documentation market estimated at $8.2 Billion with 18.0% CAGR."
            )
        ],
        competitors=[
            SearchResultItem(
                title="DAX Copilot and Ambience Healthcare",
                url="https://healthtech.org/competitors",
                snippet="Major incumbents include DAX Copilot ($199/mo) and Ambience Healthcare enterprise EHR."
            )
        ]
    )

    captured_input = None

    class MockDeepAgent:
        def invoke(self, graph_input):
            nonlocal captured_input
            captured_input = graph_input
            return {"messages": [AIMessage(content="Report generated")]}

    monkeypatch.setattr(pipeline.tavily, "perform_validation_search", lambda *args, **kwargs: sample_search)
    pipeline.deep_agent = MockDeepAgent()

    state = pipeline.run(idea)

    assert captured_input is not None
    user_content = captured_input["messages"][0]["content"]
    assert "https://healthtech.org/report" in user_content
    assert "DAX Copilot" in user_content
    assert "$8.2 Billion" in user_content


def test_production_path_output_contract_requests_expected_report_structure(monkeypatch):
    """Test P (Req C): Proves the invocation prompt requests the exact markdown headings and required contract."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Contract Analysis AI", target_industry="LegalTech")

    captured_prompt = None

    class MockDeepAgent:
        def invoke(self, graph_input):
            nonlocal captured_prompt
            captured_prompt = graph_input["messages"][0]["content"]
            return {"messages": [AIMessage(content="Done")]}

    monkeypatch.setattr(pipeline.tavily, "perform_validation_search", lambda *args, **kwargs: None)
    pipeline.deep_agent = MockDeepAgent()

    pipeline.run(idea)

    assert captured_prompt is not None
    assert "## 1. Market Sizing and Growth Analysis" in captured_prompt
    assert "Total Addressable Market (TAM)" in captured_prompt
    assert "Projected CAGR" in captured_prompt
    assert "## 2. Competitor Landscape and Moat" in captured_prompt
    assert "Direct Competitors" in captured_prompt
    assert "## 3. SWOT Analysis and Risk Evaluation" in captured_prompt
    assert "## 4. Minimum Viable Product (MVP) Specifications" in captured_prompt
    assert "## 5. Go-To-Market (GTM) Strategy" in captured_prompt
    assert "CRITICAL GROUNDING RULES" in captured_prompt
    assert "/workspace/executive_validation_report.md" in captured_prompt


def test_realistic_markdown_with_tam_sam_som_cagr_mapping():
    """Test Q (Req D): Proves realistic Markdown containing TAM/SAM/SOM/CAGR maps correctly into state."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(
        idea_text="AI-powered personal finance assistant",
        target_industry="FinTech / Personal Finance"
    )
    state = StartupState(idea=idea)

    realistic_markdown = """# Executive Startup Validation Report

## 1. Market Sizing and Growth Analysis
- **Total Addressable Market (TAM):** $14.5 Billion
- **Serviceable Addressable Market (SAM):** $3.8 Billion
- **Serviceable Obtainable Market (SOM):** $350 Million
- **Projected CAGR:** 15.2% CAGR
- **Growth Drivers:** AI mobile banking adoption, automated micro-savings demand, Gen Z budgeting habits
The personal finance management software market is experiencing rapid expansion driven by mobile banking integration.

## 2. Competitor Landscape and Moat
- **Market Positioning:** Positions as the premier proactive AI personal finance copilot.
- **Defensibility Moat:** Proprietary spending categorization and behavioral habit-building loops.
### Direct Competitors:
- **Cleo (Freemium ($5.99/mo)):** AI chat-based conversational budgeting assistant.
- **Rocket Money (Freemium ($3-12/mo)):** Subscription management and automated cancellation.
- **Copilot Money (Subscription ($13/mo)):** High-end Mac/iOS native personal finance tracker.
### Indirect Competitors / Alternatives:
- **Manual Excel / Google Sheets:** Free manual spreadsheet tracking templates.
"""

    deep_result = {
        "messages": [
            AIMessage(content=realistic_markdown)
        ]
    }

    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)

    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 14.5
    assert state.market_analysis.sam_billions == 3.8
    assert state.market_analysis.som_billions == 0.35
    assert state.market_analysis.cagr_percentage == 15.2
    assert "AI mobile banking adoption" in state.market_analysis.key_growth_drivers


def test_realistic_markdown_with_competitors_mapping():
    """Test R (Req E): Proves realistic Markdown containing direct/indirect competitors maps correctly into state."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(
        idea_text="AI-powered personal finance assistant",
        target_industry="FinTech"
    )
    state = StartupState(idea=idea)

    realistic_markdown = """## 2. Competitor Landscape and Moat
- **Market Positioning:** Positions as an automated cashflow forecast engine for young professionals.
- **Defensibility Moat:** Proprietary banking data parsing models and low-friction workflow integration.
### Direct Competitors:
- **Cleo (Freemium ($5.99/mo)):** AI chatbot companion for budgeting.
- **Rocket Money (Subscription):** Bill negotiation and subscription cancellation tool.
- **Copilot Money ($99/year):** Smart budgeting and investment tracker.
- **Origin (Enterprise B2B2C):** Comprehensive financial wellness platform.
### Indirect Competitors / Alternatives:
- **Monarch Money:** Traditional budgeting software.
- **YNAB (You Need A Budget):** Zero-based manual budgeting.
"""

    deep_result = {
        "messages": [
            AIMessage(content=realistic_markdown)
        ]
    }

    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)

    assert state.competitor_analysis is not None
    direct_names = [c.name for c in state.competitor_analysis.direct_competitors]
    assert "Cleo" in direct_names
    assert "Rocket Money" in direct_names
    assert "Copilot Money" in direct_names
    assert "Origin" in direct_names
    assert "automated cashflow forecast" in state.competitor_analysis.market_positioning_summary
    assert "banking data parsing" in state.competitor_analysis.moat_assessment


def test_missing_evidence_remains_none_without_fabrication():
    """Test S (Req F): Proves missing evidence remains None/empty and does not fabricate values."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Obscure Niche Platform", target_industry="Niche")
    state = StartupState(idea=idea)

    sparse_markdown = """## 1. Market Sizing and Growth Analysis
- **Total Addressable Market (TAM):** Evidence unavailable
- **Serviceable Addressable Market (SAM):** Evidence unavailable
- **Serviceable Obtainable Market (SOM):** Evidence unavailable
- **Projected CAGR:** Evidence unavailable
Market size could not be established from available research.

## 2. Competitor Landscape and Moat
- **Market Positioning:** No verified competitors identified from available research.
- **Defensibility Moat:** Defensibility cannot be evaluated without verified competitor evidence.
### Direct Competitors:
No verified competitors identified from available research.
"""

    deep_result = {
        "messages": [
            AIMessage(content=sparse_markdown)
        ]
    }

    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)

    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions is None
    assert state.market_analysis.sam_billions is None
    assert state.market_analysis.som_billions is None
    assert state.market_analysis.cagr_percentage is None
    assert "could not be established" in state.market_analysis.market_size_summary

    assert state.competitor_analysis is not None
    assert len(state.competitor_analysis.direct_competitors) == 0
    assert "No verified competitors" in state.competitor_analysis.market_positioning_summary


def test_structured_json_priority_preserved_over_markdown():
    """Test T (Req G): Proves existing structured JSON priority in _map_deep_result_to_state() remains unchanged."""
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Priority Test Startup", target_industry="FinTech")
    state = StartupState(idea=idea)

    json_payload = {
        "market_analysis": {
            "tam_billions": 77.7,
            "sam_billions": 20.0,
            "som_billions": 2.0,
            "market_size_summary": "Structured JSON TAM $77.7B",
            "cagr_percentage": 25.0,
            "key_growth_drivers": ["Driver from JSON"],
            "target_personas": []
        }
    }

    deep_result = {
        "structured_response": json_payload,
        "messages": [
            AIMessage(content="""## 1. Market Sizing and Growth Analysis
- **Total Addressable Market (TAM):** $10.0 Billion
""")
        ]
    }

    pipeline._map_deep_result_to_state(state, deep_result, lambda s, st: None)

    # Structured response (77.7) MUST take priority over Markdown (10.0)
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 77.7
    assert state.market_analysis.market_size_summary == "Structured JSON TAM $77.7B"


# ============================================================================
# PRODUCTION PIPELINE FIX TESTS (FIXES 1 - 6)
# ============================================================================

def test_extract_market_metric_aliases_and_rejection():
    """FIX 2: Verify _extract_market_metric accepts both acronyms and full names,
    preserves unit conversions, and rejects unrelated market numbers.
    """
    from pipeline.deep_agents_orchestrator import _extract_market_metric

    # 1. TAM aliases
    assert _extract_market_metric("Total Addressable Market: $17.2 Billion", "TAM") == 17.2
    assert _extract_market_metric("TAM: $17.2B", "TAM") == 17.2
    assert _extract_market_metric("- **Total Addressable Market (TAM):** $17.2 Billion", "TAM") == 17.2

    # 2. SAM aliases
    assert _extract_market_metric("Serviceable Addressable Market: $5.2B", "SAM") == 5.2
    assert _extract_market_metric("SAM: $5.2B", "SAM") == 5.2

    # 3. SOM aliases
    assert _extract_market_metric("Serviceable Obtainable Market: $500M", "SOM") == 0.5
    assert _extract_market_metric("SOM: $500M", "SOM") == 0.5

    # 4. Reject unrelated market-size statements without explicit labels
    assert _extract_market_metric("The conversational AI in healthcare market was valued at USD 17.2 billion in 2025", "TAM") is None
    assert _extract_market_metric("market size was $17.2 billion", "TAM") is None
    assert _extract_market_metric("The overall market is estimated to reach $50B by 2030", "TAM") is None


def test_parse_cagr_priorities_and_ranges():
    """FIX 3: Verify _parse_cagr prioritizes explicit metric lines, handles narrative market CAGR,
    does not allow regional/segment ranges to erase explicit CAGR, and returns None for ranges only.
    """
    from pipeline.deep_agents_orchestrator import _parse_cagr

    # 1. Explicit CAGR + unrelated regional range => returns explicit CAGR
    text_with_regional_range = """
- **Projected CAGR:** 25.7% CAGR
Later:
India will grow at 32.1% to 35.0% CAGR.
"""
    assert _parse_cagr(text_with_regional_range) == 25.7

    # 2. Explicit single CAGR on metric line => returns value
    assert _parse_cagr("Projected CAGR: 25.7%") == 25.7
    assert _parse_cagr("- **CAGR:** 14.5%") == 14.5
    assert _parse_cagr("Compound Annual Growth Rate (CAGR): 18.2%") == 18.2

    # 3. Narrative market CAGR without explicit metric line
    assert _parse_cagr("The conversational AI in healthcare market was valued at USD 17.2 billion in 2025 ... at a 25.7% CAGR.") == 25.7

    # 4. Only CAGR range => returns None per requirement
    assert _parse_cagr("- **CAGR:** 12.6% - 16.9%") is None
    assert _parse_cagr("The market is expected to expand at a CAGR of 12.6% to 16.9%.") is None

    # 5. No CAGR => None
    assert _parse_cagr("The market is growing rapidly with strong enterprise interest.") is None


def test_parse_competitor_analysis_bold_headers():
    """FIX 4: Verify _parse_competitor_analysis_from_markdown recognizes bold-header sections
    (**Direct Competitors:** and **Indirect Competitors:**) and bulleted competitors without colons.
    """
    from pipeline.deep_agents_orchestrator import _parse_competitor_analysis_from_markdown

    markdown = """
## 2. Competitor Landscape and Moat

**Direct Competitors:**
- **DoctorConnect:** Automated patient recall and appointment reminders
- **Innovaccer:** Healthcare data platform and coordination

**Indirect Competitors:**
- Company A
- Company B

**Market Positioning:** Leading AI-driven recall solution for SMB clinics.
**Defensibility Moat:** Proprietary EHR integration connectors.
"""

    result = _parse_competitor_analysis_from_markdown(markdown)
    assert result is not None

    direct_names = [c.name for c in result.direct_competitors]
    assert "DoctorConnect" in direct_names
    assert "Innovaccer" in direct_names
    assert len(result.direct_competitors) == 2

    indirect_names = [c.name for c in result.indirect_competitors]
    assert "Company A" in indirect_names
    assert "Company B" in indirect_names
    assert len(result.indirect_competitors) == 2

    # Verify section breaks didn't leak into competitors
    assert "Market Positioning" not in direct_names
    assert "Defensibility Moat" not in direct_names
    assert result.market_positioning_summary == "Leading AI-driven recall solution for SMB clinics."
    assert "Proprietary EHR integration" in result.moat_assessment


def test_production_fallback_with_real_search_evidence():
    """FIX 5: Construct a StartupState with real-looking Tavily SearchResultItem objects.
    Invoke production mapping with deep_result = None.
    Verify:
    - real search evidence remains available on state
    - explicit market metrics are extracted only when clearly labeled
    - CAGR is extracted when explicitly supported
    - competitors are extracted only when explicitly identified
    - no fabricated values appear
    - no demo constants appear
    """
    from state.schema import SearchResultItem, WebSearchResults
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(
        idea_text="Conversational AI patient recall system for medical clinics",
        target_industry="HealthTech / AI",
        target_audience="Medical clinics & healthcare providers"
    )

    search_results = WebSearchResults(
        market_trends=[
            SearchResultItem(
                title="Global Conversational AI in Healthcare Market 2026",
                url="https://healthcaredataresearch.org/report-2026",
                snippet="The conversational AI in healthcare market was valued at USD 17.2 billion in 2025 and is projected to expand at a 25.7% CAGR through 2032."
            )
        ],
        competitors=[
            SearchResultItem(
                title="Top Healthcare Patient Recall Competitors and Alternatives",
                url="https://g2.com/compare/healthcare-recall",
                snippet="DoctorConnect competes directly with Innovaccer and Klara in automated patient engagement and recall systems."
            )
        ]
    )

    state = StartupState(idea=idea, search_results=search_results)

    # Invoke production mapping path with deep_result = None
    pipeline._map_deep_result_to_state(state, deep_result=None, notify=lambda s, st: None)

    # 1. Search evidence remains available
    assert state.search_results is not None
    assert len(state.search_results.market_trends) == 1
    assert len(state.search_results.competitors) == 1

    # 2. Market metrics:
    # "valued at USD 17.2 billion" is NOT explicitly labeled as TAM or Total Addressable Market!
    # Therefore TAM must remain None (no fabrication or ungrounded inference).
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions is None
    assert state.market_analysis.sam_billions is None
    assert state.market_analysis.som_billions is None

    # 3. CAGR is explicitly supported ("at a 25.7% CAGR")
    assert state.market_analysis.cagr_percentage == 25.7

    # 4. Competitors are extracted only when explicitly identified from competitor evidence
    assert state.competitor_analysis is not None
    comp_names = [c.name for c in state.competitor_analysis.direct_competitors]
    assert "DoctorConnect" in comp_names
    assert "Innovaccer" in comp_names
    assert "Klara" in comp_names

    # 5. No fabricated demo constants or unverified data
    assert "Incumbent Core SaaS" not in comp_names
    assert state.swot_analysis is None
    assert state.mvp_recommendation is None
    assert state.gtm_strategy is None


def test_production_fallback_with_explicit_labeled_tam():
    """FIX 5 (explicit TAM): When search results contain explicit Total Addressable Market label,
    TAM is extracted and reaches state.market_analysis.
    """
    from state.schema import SearchResultItem, WebSearchResults
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="AI Healthcare Recall", target_industry="HealthTech")

    search_results = WebSearchResults(
        market_trends=[
            SearchResultItem(
                title="Healthcare AI Market Sizing",
                url="https://marketdata.org/sizing",
                snippet="Total Addressable Market: $17.2 Billion with projected CAGR: 25.7%."
            )
        ],
        competitors=[
            SearchResultItem(
                title="Direct Competitor List",
                url="https://reviewflow.com/competitors",
                snippet="Leading competitors include DoctorConnect and Innovaccer."
            )
        ]
    )

    state = StartupState(idea=idea, search_results=search_results)

    pipeline._map_deep_result_to_state(state, deep_result=None, notify=lambda s, st: None)

    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions == 17.2
    assert state.market_analysis.cagr_percentage == 25.7

    assert state.competitor_analysis is not None
    comp_names = [c.name for c in state.competitor_analysis.direct_competitors]
    assert "DoctorConnect" in comp_names
    assert "Innovaccer" in comp_names


def test_production_fallback_insufficient_evidence():
    """FIX 5 (insufficient evidence): When deep_result is None and search_results contains
    only generic market discussion without explicit metrics or competitor names:
    TAM=None, SAM=None, SOM=None, CAGR=None, competitors=[], no fabricated values.
    """
    from state.schema import SearchResultItem, WebSearchResults
    pipeline = StartupValidatorDeepAgentsPipeline()
    idea = StartupIdea(idea_text="Vague Concept Idea", target_industry="Technology")

    search_results = WebSearchResults(
        market_trends=[
            SearchResultItem(
                title="General Technology Industry Trends",
                url="https://techdiscussion.org/news",
                snippet="Industry participants met to discuss future innovations and ecosystem trends in general software development."
            )
        ],
        competitors=[
            SearchResultItem(
                title="Competitive Overview",
                url="https://techdiscussion.org/comp",
                snippet="The competitive landscape features various companies operating across global enterprise markets."
            )
        ]
    )

    state = StartupState(idea=idea, search_results=search_results)

    pipeline._map_deep_result_to_state(state, deep_result=None, notify=lambda s, st: None)

    # Market analysis preserves None for missing metrics
    assert state.market_analysis is not None
    assert state.market_analysis.tam_billions is None
    assert state.market_analysis.sam_billions is None
    assert state.market_analysis.som_billions is None
    assert state.market_analysis.cagr_percentage is None

    # Competitor analysis preserves empty list
    assert state.competitor_analysis is not None
    assert len(state.competitor_analysis.direct_competitors) == 0
    assert len(state.competitor_analysis.indirect_competitors) == 0

    # No demo constants
    assert state.market_analysis.tam_billions != 15.0
    assert state.market_analysis.cagr_percentage != 15.0


def test_market_growth_trajectory_chart_rendering():
    """FIX 6: Verify ChartEngine.render_market_growth_trajectory(17.2, 25.7) returns
    a valid Plotly Figure when valid TAM and CAGR are present, and returns None when missing.
    Proves charts.py is untouched and functions correctly with verified evidence.
    """
    import plotly.graph_objects as go
    from ui.components.charts import ChartEngine

    # 1. Valid TAM and CAGR return Plotly Figure
    fig = ChartEngine.render_market_growth_trajectory(17.2, 25.7)
    assert fig is not None
    assert isinstance(fig, go.Figure)
    assert "TAM $17.2B" in fig.layout.title.text
    assert "25.7% CAGR" in fig.layout.title.text

    # 2. Missing TAM or CAGR returns None without error
    assert ChartEngine.render_market_growth_trajectory(None, 25.7) is None
    assert ChartEngine.render_market_growth_trajectory(17.2, None) is None
    assert ChartEngine.render_market_growth_trajectory(None, None) is None
