import logging
from typing import Callable, Optional, List, Dict, Any
from deepagents import create_deep_agent, SubAgent
from langchain_google_genai import ChatGoogleGenerativeAI

from state.schema import (
    StartupState,
    StartupIdea,
    DeepAgentsPlan,
    MarketAnalysis,
    CompetitorAnalysis,
    SWOTAnalysis,
    MVPRecommendation,
    GTMStrategy,
    ValidationReport
)
from tools.planning_tool import DeepAgentsPlanner
from tools.tavily_tool import tavily_search_tool, TavilySearchTool
from agents.market_analysis_agent import MarketAnalysisAgent
from agents.competitor_agent import CompetitorAgent
from agents.swot_risk_agent import SWOTRiskAgent
from agents.mvp_recommendation_agent import MVPRecommendationAgent
from agents.gtm_strategy_agent import GTMStrategyAgent
from agents.report_agent import ReportAgent
from app.config import config
from services.logger import get_logger

logger = get_logger(__name__)


class StartupValidatorDeepAgentsPipeline:
    """Official Deep Agents Framework Pipeline for Startup Idea Validation.
    
    Orchestrates the validation flow using Deep Agents framework subagents
    and scoped context engineering.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or config.DEFAULT_MODEL

        # Specialized business agents
        self.planner = DeepAgentsPlanner(model_name=self.model_name)
        self.market_agent = MarketAnalysisAgent(model_name=self.model_name)
        self.competitor_agent = CompetitorAgent(model_name=self.model_name)
        self.swot_agent = SWOTRiskAgent(model_name=self.model_name)
        self.mvp_agent = MVPRecommendationAgent(model_name=self.model_name)
        self.gtm_agent = GTMStrategyAgent(model_name=self.model_name)
        self.report_agent = ReportAgent(model_name=self.model_name)

        # 1. Define SubAgents using official Deep Agents SubAgent spec format
        self.subagents: List[SubAgent] = [
            {
                "name": "market-research",
                "description": "Researches market size (TAM, SAM, SOM), CAGR, market trends, and growth drivers.",
                "system_prompt": "You are a Market Research Subagent. Evaluate market size, CAGR, growth drivers, and target customer personas.",
                "tools": [tavily_search_tool],
            },
            {
                "name": "competitor-research",
                "description": "Finds direct and indirect competitors, feature comparisons, pricing models, and defensibility moats.",
                "system_prompt": "You are a Competitor Research Subagent. Map the competitive landscape, direct incumbents, and defensibility moats.",
                "tools": [tavily_search_tool],
            },
            {
                "name": "swot-risk",
                "description": "Evaluates strengths, weaknesses, opportunities, threats, and severity risk matrix.",
                "system_prompt": "You are a SWOT & Risk Subagent. Formulate a SWOT analysis and severity risk matrix with mitigations.",
                "tools": [],
            },
            {
                "name": "mvp",
                "description": "Scopes core MVP features, technology stack, 4-week roadmap, and key metrics/KPIs.",
                "system_prompt": "You are an MVP Scoping Subagent. Define core value proposition, tech architecture, feature breakdown, and roadmap.",
                "tools": [],
            },
            {
                "name": "gtm",
                "description": "Formulates customer acquisition channels, positioning statement, pricing strategy, and launch tactics.",
                "system_prompt": "You are a Go-To-Market Strategy Subagent. Recommend primary acquisition channels, positioning, and launch strategy.",
                "tools": [],
            },
            {
                "name": "report",
                "description": "Synthesizes comprehensive validation report, overall viability index, and strategic verdict.",
                "system_prompt": "You are a Lead Executive Report Subagent. Compile all validation findings, calculate viability score, and output executive summary.",
                "tools": [],
            }
        ]

        # 2. Construct Main Deep Agent graph using official deepagents API
        try:
            self.model = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=config.GEMINI_API_KEY or "not_configured"
            )
            self.deep_agent = create_deep_agent(
                model=self.model,
                subagents=self.subagents,
                system_prompt="You are the Main Startup Validator Deep Agent responsible for orchestrating multi-agent startup idea validation."
            )
            logger.info("Official Deep Agents Main Validator Agent initialized successfully.")
        except Exception as e:
            logger.warning(f"Deep Agents Graph compilation warning: {e}. Pipeline operating in fallback mode.")
            self.deep_agent = None

    def run(self, idea: StartupIdea, progress_callback: Optional[Callable[[str, str], None]] = None) -> StartupState:
        state = StartupState(idea=idea, status="initialized")

        def notify(step: str, status: str):
            if progress_callback:
                progress_callback(step, status)
            logger.info(f"Deep Agents Pipeline Step [{step}] -> {status}")

        try:
            # Step 0: Strategic Research Planning
            notify("planner", "in_progress")
            state.planning_output = self.planner.plan_validation(idea)
            notify("planner", "completed")

            # Step 1: Market Research Subagent Context & Execution
            # Context: startup idea, industry, target_audience, business_model, budget, timeline
            notify("web_search", "in_progress")
            notify("market_analysis", "in_progress")
            state = self.market_agent.run(state)
            notify("web_search", "completed")
            notify("market_analysis", "completed")

            # Step 2: Competitor Research Subagent Context & Execution
            # Context: startup idea, industry, target_audience, market_analysis
            notify("competitor_analysis", "in_progress")
            state = self.competitor_agent.run(state)
            notify("competitor_analysis", "completed")

            # Step 3: SWOT & Risk Subagent Context & Execution
            # Context: startup idea, market_research, competitor_research
            notify("swot_risk", "in_progress")
            state = self.swot_agent.run(state)
            notify("swot_risk", "completed")

            # Step 4: MVP Subagent Context & Execution
            # Context: startup idea, market_analysis, competitor_analysis, SWOT
            notify("mvp_recommendation", "in_progress")
            state = self.mvp_agent.run(state)
            notify("mvp_recommendation", "completed")

            # Step 5: GTM Subagent Context & Execution
            # Context: startup idea, market_analysis, competitor_analysis, MVP, SWOT
            notify("gtm_strategy", "in_progress")
            state = self.gtm_agent.run(state)
            notify("gtm_strategy", "completed")

            # Step 6: Final Executive Report Subagent Context & Execution
            # Context: all relevant validated information + deterministic scoring
            notify("report", "in_progress")
            state = self.report_agent.run(state)
            notify("report", "completed")

            state.status = "completed"
            return state

        except Exception as e:
            logger.exception(f"Deep Agents Pipeline execution failed: {e}")
            state.status = "error"
            state.error = str(e)
            return state
