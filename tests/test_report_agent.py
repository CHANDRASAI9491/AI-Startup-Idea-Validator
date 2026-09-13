import pytest
from state.schema import StartupState, StartupIdea
from agents.report_agent import ReportAgent


def test_report_agent():
    agent = ReportAgent()
    state = StartupState(idea=StartupIdea(idea_text="AI Startup Validator"))
    updated_state = agent.run(state)
    assert updated_state.final_report is not None
    assert 0 <= updated_state.final_report.overall_viability_score <= 100
    assert updated_state.final_report.verdict in ["PROCEED", "PIVOT", "CAUTION", "STOP"]


def test_report_agent_prompt_no_fabricated_15b_example():
    """Verify that prompts/report_agent.md contains no $15.0B example claim."""
    with open("prompts/report_agent.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "$15.0B" not in content
    assert "15.0B" not in content
    assert "Validated market demand indicates meaningful expansion potential" in content


def test_market_growth_chart_and_report_rendering_none_defensive():
    """Verify defensive handling when market TAM or CAGR is None.
    ChartEngine must return None and render_report_viewer must not raise TypeError.
    """
    from ui.components.charts import ChartEngine
    from ui.components.report_viewer import render_report_viewer
    from state.schema import MarketAnalysis

    # 1. Chart engine must return None when TAM or CAGR is None, without TypeError
    assert ChartEngine.render_market_growth_trajectory(None, None) is None
    assert ChartEngine.render_market_growth_trajectory(10.0, None) is None
    assert ChartEngine.render_market_growth_trajectory(None, 15.0) is None

    # Valid values should still return a Plotly Figure
    fig = ChartEngine.render_market_growth_trajectory(10.0, 15.0)
    assert fig is not None

    # 2. Report viewer rendering must not raise TypeError when TAM and CAGR are None
    state = StartupState(
        idea=StartupIdea(idea_text="Defensive Chart Test"),
        market_analysis=MarketAnalysis(
            tam_billions=None,
            sam_billions=None,
            som_billions=None,
            cagr_percentage=None,
            market_size_summary="Market evidence unavailable.",
        )
    )
    # Rendering should succeed without TypeError
    render_report_viewer(state)


def test_missing_swot_mvp_gtm_does_not_crash_downstream_report_generation(tmp_path):
    """Verify that downstream exports (Markdown, JSON, PDF) and UI report viewer
    safely handle None for swot_analysis, mvp_recommendation, gtm_strategy, and search_results."""
    from tools.file_tools import FileTools
    from services.scoring_engine import DeterministicScoringEngine
    from state.schema import ValidationReport, MarketAnalysis, CompetitorAnalysis
    from ui.components.report_viewer import render_report_viewer

    idea = StartupIdea(
        idea_text="AI Healthcare Logistics",
        target_industry="HealthTech",
        target_audience="Hospitals",
        business_model="B2B SaaS"
    )
    scoring = DeterministicScoringEngine.calculate_scores(
        idea_text=idea.idea_text,
        target_industry=idea.target_industry,
        tam_billions=None,
        cagr_percentage=None,
        direct_competitor_count=None,
        financial_risk=5,
        technical_risk=5,
        regulatory_risk=4
    )
    scoring.evidence_limitations.append("SWOT and risk analysis could not be verified from available research.")
    scoring.evidence_limitations.append("Live web research was unavailable; market and competitor intelligence could not be verified in real time.")

    report = ValidationReport(
        overall_viability_score=scoring.total_viability_score,
        verdict=scoring.verdict,
        executive_summary="Executive summary with unavailable evidence.",
        scoring_breakdown=scoring,
        market_score=int((scoring.market_opportunity_score / 20.0) * 100),
        competitor_score=int((scoring.competition_score / 15.0) * 100),
        risk_score=int((scoring.execution_risk_score / 10.0) * 100),
        mvp_score=int((scoring.technical_feasibility_score / 10.0) * 100),
        gtm_score=int((scoring.scalability_score / 15.0) * 100),
        key_takeaways=["Key finding 1", "Key finding 2"],
        recommended_next_steps=["Step 1", "Step 2"]
    )

    state = StartupState(
        idea=idea,
        market_analysis=MarketAnalysis(tam_billions=None, cagr_percentage=None),
        competitor_analysis=CompetitorAnalysis(direct_competitors=[]),
        swot_analysis=None,
        mvp_recommendation=None,
        gtm_strategy=None,
        search_results=None,
        final_report=report
    )

    # 1. Markdown Export
    md_path = str(tmp_path / "report.md")
    md_content = FileTools.export_report_markdown(state, md_path)
    assert "Evidence unavailable: SWOT and risk analysis" in md_content
    assert "Evidence unavailable: MVP recommendations" in md_content
    assert "Evidence unavailable: GTM strategy" in md_content
    assert "Evidence unavailable: Live web research" in md_content
    assert "$None" not in md_content
    assert "None%" not in md_content

    # 2. JSON Export
    json_path = str(tmp_path / "report.json")
    FileTools.export_report_json(state, json_path)
    import json
    with open(json_path, "r", encoding="utf-8") as f:
        parsed = json.load(f)
    assert parsed["swot_analysis"] is None
    assert parsed["mvp_recommendation"] is None
    assert parsed["gtm_strategy"] is None

    # 3. PDF Export
    pdf_path = str(tmp_path / "report.pdf")
    pdf_res = FileTools.export_report_pdf(state, pdf_path)
    assert pdf_res == pdf_path
    import os
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000

    # 4. Streamlit Report Viewer Component
    render_report_viewer(state)
