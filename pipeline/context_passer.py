from typing import Dict, Any, Optional
from state.schema import AgentState, StartupIdea


class ContextPasser:
    """Manages state mutations and data propagation between pipeline steps."""

    @staticmethod
    def initialize_state(idea: StartupIdea) -> AgentState:
        return AgentState(idea=idea, status="initialized")

    @staticmethod
    def update_search_results(state: AgentState, search_results: Any) -> AgentState:
        state.search_results = search_results
        state.status = "search_completed"
        return state

    @staticmethod
    def update_analyses(
        state: AgentState,
        market: Any,
        competitors: Any,
        swot: Any,
        mvp: Any,
        gtm: Any
    ) -> AgentState:
        state.market_analysis = market
        state.competitor_analysis = competitors
        state.swot_analysis = swot
        state.mvp_recommendation = mvp
        state.gtm_strategy = gtm
        state.status = "analyses_completed"
        return state

    @staticmethod
    def set_final_report(state: AgentState, report: Any) -> AgentState:
        state.final_report = report
        state.status = "completed"
        return state
