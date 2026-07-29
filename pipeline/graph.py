import logging
from typing import Callable, Optional
from langgraph.graph import StateGraph, START, END
from state.schema import StartupState, StartupIdea, AgentState
from agents.web_search_agent import WebSearchAgent
from agents.market_analysis_agent import MarketAnalysisAgent
from agents.competitor_agent import CompetitorAgent
from agents.swot_risk_agent import SWOTRiskAgent
from agents.mvp_recommendation_agent import MVPRecommendationAgent
from agents.gtm_strategy_agent import GTMStrategyAgent
from agents.report_agent import ReportAgent

logger = logging.getLogger(__name__)


class ValidationGraph:
    """LangGraph Multi-Agent StateGraph Orchestrator for startup validation."""

    def __init__(self):
        self.web_search_agent = WebSearchAgent()
        self.market_agent = MarketAnalysisAgent()
        self.competitor_agent = CompetitorAgent()
        self.swot_agent = SWOTRiskAgent()
        self.mvp_agent = MVPRecommendationAgent()
        self.gtm_agent = GTMStrategyAgent()
        self.report_agent = ReportAgent()

        self._compiled_graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(StartupState)

        # Define nodes for each agent step
        workflow.add_node("web_search", self.web_search_agent.run)
        workflow.add_node("market_analysis", self.market_agent.run)
        workflow.add_node("competitor_analysis", self.competitor_agent.run)
        workflow.add_node("swot_risk", self.swot_agent.run)
        workflow.add_node("mvp_recommendation", self.mvp_agent.run)
        workflow.add_node("gtm_strategy", self.gtm_agent.run)
        workflow.add_node("report", self.report_agent.run)

        # Define edge transitions
        workflow.add_edge(START, "web_search")
        workflow.add_edge("web_search", "market_analysis")
        workflow.add_edge("market_analysis", "competitor_analysis")
        workflow.add_edge("competitor_analysis", "swot_risk")
        workflow.add_edge("swot_risk", "mvp_recommendation")
        workflow.add_edge("mvp_recommendation", "gtm_strategy")
        workflow.add_edge("gtm_strategy", "report")
        workflow.add_edge("report", END)

        return workflow.compile()

    def run(self, idea: StartupIdea, progress_callback: Optional[Callable[[str, str], None]] = None) -> StartupState:
        initial_state = StartupState(idea=idea, status="initialized")

        def notify(step: str, status: str):
            if progress_callback:
                progress_callback(step, status)
            logger.info(f"LangGraph Pipeline Step [{step}] -> {status}")

        try:
            notify("web_search", "in_progress")
            state = self.web_search_agent.run(initial_state)
            notify("web_search", "completed")

            notify("market_analysis", "in_progress")
            state = self.market_agent.run(state)
            notify("market_analysis", "completed")

            notify("competitor_analysis", "in_progress")
            state = self.competitor_agent.run(state)
            notify("competitor_analysis", "completed")

            notify("swot_risk", "in_progress")
            state = self.swot_agent.run(state)
            notify("swot_risk", "completed")

            notify("mvp_recommendation", "in_progress")
            state = self.mvp_agent.run(state)
            notify("mvp_recommendation", "completed")

            notify("gtm_strategy", "in_progress")
            state = self.gtm_agent.run(state)
            notify("gtm_strategy", "completed")

            notify("report", "in_progress")
            state = self.report_agent.run(state)
            notify("report", "completed")

            return state

        except Exception as e:
            logger.exception(f"LangGraph execution failed: {e}")
            initial_state.status = "error"
            initial_state.error = str(e)
            return initial_state
