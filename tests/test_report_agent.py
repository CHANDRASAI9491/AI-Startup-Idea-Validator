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
