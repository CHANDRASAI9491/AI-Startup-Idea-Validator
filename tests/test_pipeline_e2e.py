import pytest
from app.orchestrator import ApplicationOrchestrator


def test_end_to_end_validation_pipeline():
    orchestrator = ApplicationOrchestrator()
    state = orchestrator.validate_idea(
        idea_text="AI-powered personalized meal planning app",
        target_industry="HealthTech",
        target_audience="Busy professionals",
        session_id="test_e2e_session"
    )

    assert state is not None
    assert state.status == "completed"
    assert state.final_report is not None
    assert 0 <= state.final_report.overall_viability_score <= 100
    assert state.final_report.verdict in ["PROCEED", "PIVOT", "CAUTION", "STOP"]
    assert state.market_analysis is not None
    assert state.competitor_analysis is not None
    assert state.swot_analysis is not None
    assert state.mvp_recommendation is not None
    assert state.gtm_strategy is not None

    # Test Q&A Advisor
    answer = orchestrator.ask_advisor("test_e2e_session", "What is the biggest risk?", [])
    assert answer is not None
    assert len(answer) > 10
