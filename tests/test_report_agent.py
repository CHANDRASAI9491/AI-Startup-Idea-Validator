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

