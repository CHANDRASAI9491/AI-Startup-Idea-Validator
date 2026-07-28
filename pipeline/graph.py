import logging
from typing import Callable, Optional
from state.schema import AgentState, StartupIdea
from agents.web_search_agent import WebSearchAgent
from agents.market_analysis_agent import MarketAnalysisAgent
from agents.competitor_agent import CompetitorAgent
from agents.swot_risk_agent import SWOTRiskAgent
from agents.mvp_recommendation_agent import MVPRecommendationAgent
from agents.gtm_strategy_agent import GTMStrategyAgent
from agents.report_agent import ReportAgent
from pipeline.context_passer import ContextPasser

logger = logging.getLogger(__name__)


class ValidationGraph:
    """DAG Pipeline Orchestrator for multi-agent validation."""

    def __init__(self):
        self.web_search_agent = WebSearchAgent()
        self.market_agent = MarketAnalysisAgent()
        self.competitor_agent = CompetitorAgent()
        self.swot_agent = SWOTRiskAgent()
        self.mvp_agent = MVPRecommendationAgent()
        self.gtm_agent = GTMStrategyAgent()
        self.report_agent = ReportAgent()

    def run(self, idea: StartupIdea, progress_callback: Optional[Callable[[str, str], None]] = None) -> AgentState:
        state = ContextPasser.initialize_state(idea)

        def notify(step: str, status: str):
            if progress_callback:
                progress_callback(step, status)
            logger.info(f"Graph Pipeline [{step}] -> {status}")

        try:
            # Step 1: Web Research
            notify("web_search", "in_progress")
            search_results = self.web_search_agent.run(idea)
            state = ContextPasser.update_search_results(state, search_results)
            notify("web_search", "completed")

            # Step 2: Parallel / Sequential Domain Analysis
            notify("market_analysis", "in_progress")
            market = self.market_agent.run(idea, search_results)
            notify("market_analysis", "completed")

            notify("competitor_analysis", "in_progress")
            competitors = self.competitor_agent.run(idea, search_results)
            notify("competitor_analysis", "completed")

            notify("swot_risk", "in_progress")
            swot = self.swot_agent.run(idea, search_results)
            notify("swot_risk", "completed")

            notify("mvp_recommendation", "in_progress")
            mvp = self.mvp_agent.run(idea)
            notify("mvp_recommendation", "completed")

            notify("gtm_strategy", "in_progress")
            gtm = self.gtm_agent.run(idea)
            notify("gtm_strategy", "completed")

            state = ContextPasser.update_analyses(state, market, competitors, swot, mvp, gtm)

            # Step 3: Synthesis & Report Generation
            notify("final_report", "in_progress")
            report = self.report_agent.run(idea, market, competitors, swot, mvp, gtm)
            state = ContextPasser.set_final_report(state, report)
            notify("final_report", "completed")

            return state

        except Exception as e:
            logger.exception(f"Pipeline execution failed: {e}")
            state.status = "error"
            state.error = str(e)
            return state
