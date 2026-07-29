from typing import Dict, Any, Optional
from state.schema import StartupState, StartupIdea, AgentState


class ContextPasser:
    """Manages state mutations and data propagation between pipeline steps."""

    @staticmethod
    def initialize_state(idea: StartupIdea) -> StartupState:
        return StartupState(idea=idea, status="initialized")

    @staticmethod
    def update_search_results(state: StartupState, search_results: Any) -> StartupState:
        state.search_results = search_results
        state.status = "search_completed"
        return state

    @staticmethod
    def update_analyses(
        state: StartupState,
        market: Any = None,
        competitors: Any = None,
        swot: Any = None,
        mvp: Any = None,
        gtm: Any = None
    ) -> StartupState:
        if market:
            state.market_analysis = market
        if competitors:
            state.competitor_analysis = competitors
        if swot:
            state.swot_analysis = swot
        if mvp:
            state.mvp_recommendation = mvp
        if gtm:
            state.gtm_strategy = gtm
        state.status = "analyses_completed"
        return state

    @staticmethod
    def set_final_report(state: StartupState, report: Any) -> StartupState:
        state.final_report = report
        state.status = "completed"
        return state
