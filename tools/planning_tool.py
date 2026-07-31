import logging
from typing import List, Dict, Any, Optional
from state.schema import StartupIdea, DeepAgentsPlan
from services.llm_service import LLMService

logger = logging.getLogger(__name__)


class DeepAgentsPlanner:
    """DeepAgents Planner that analyzes startup concepts and generates an execution plan before graph orchestration."""

    def __init__(self, model_name: Optional[str] = None):
        self.llm_service = LLMService(model_name=model_name)

    def plan_validation(self, idea: StartupIdea) -> DeepAgentsPlan:
        logger.info(f"DeepAgentsPlanner generating execution plan for idea: {idea.idea_text}")

        prompt = f"""
Create a strategic multi-agent validation plan for this startup concept.

Startup Description: {idea.idea_text}
Industry Sector: {idea.target_industry}
Target Audience: {idea.target_audience}
Business Model: {idea.business_model}

Respond ONLY with a JSON object matching this structure:
{{
  "strategic_objective": "Validate market demand, competitive defensibility, and financial risk for the concept.",
  "research_questions": [
    "What is the total addressable market size and CAGR for this domain?",
    "Who are the key direct and indirect incumbents?",
    "What technical and regulatory risks exist?",
    "What is the optimal MVP feature scope and launch timeline?"
  ],
  "agent_allocations": {{
    "WebSearchAgent": "Gather targeted web snippets for market trends, competitors, and pain points.",
    "MarketAnalysisAgent": "Quantify TAM/SAM/SOM, CAGR, and build target customer personas.",
    "CompetitorAgent": "Evaluate incumbent features, positioning, and competitive moat.",
    "SWOTRiskAgent": "Assess strengths, weaknesses, opportunities, threats, and risk scores.",
    "MVPRecommendationAgent": "Define core value proposition, tech stack, and 4-week roadmap.",
    "GTMStrategyAgent": "Formulate acquisition channels, pricing model, and launch tactics.",
    "ReportAgent": "Synthesize all agent findings into an executive viability score and verdict."
  }}
}}
"""
        json_data = self.llm_service.generate_json(prompt, system_instruction="You are a Chief AI Architect and Strategic Planner.")

        if json_data:
            try:
                return DeepAgentsPlan.model_validate(json_data)
            except Exception as e:
                logger.warning(f"DeepAgentsPlan parsing error: {e}")

        # Fallback deterministic execution plan
        return DeepAgentsPlan(
            strategic_objective=f"Conduct multi-agent validation and risk analysis for '{idea.idea_text}' within {idea.target_industry}.",
            research_questions=[
                f"What is the total addressable market size and CAGR in {idea.target_industry}?",
                f"Who are the main direct and indirect competitors targeting {idea.target_audience}?",
                "What are the key technical, financial, and regulatory risks?",
                "What MVP feature scope can be built within the target budget and timeline?"
            ],
            agent_allocations={
                "WebSearchAgent": "Gather multi-category web search data across market trends and competitors.",
                "MarketAnalysisAgent": "Quantify TAM/SAM/SOM market sizes and customer personas.",
                "CompetitorAgent": "Map incumbent strengths, weaknesses, and market positioning.",
                "SWOTRiskAgent": "Calculate financial, technical, and regulatory risk scores.",
                "MVPRecommendationAgent": "Scope core value proposition, tech stack, and roadmap.",
                "GTMStrategyAgent": "Define primary customer acquisition channels and pricing.",
                "ReportAgent": "Synthesize comprehensive executive report and final verdict."
            }
        )


class PlanningTool:
    """Tracks task planning and execution steps for multi-agent validation."""

    def __init__(self):
        self.steps = [
            {"id": "planner", "name": "DeepAgents Strategic Research Planning", "status": "pending"},
            {"id": "web_search", "name": "Web Research and Market Data Gathering", "status": "pending"},
            {"id": "market_analysis", "name": "TAM/SAM/SOM and Market Size Evaluation", "status": "pending"},
            {"id": "competitor_analysis", "name": "Competitive Matrix and Moat Mapping", "status": "pending"},
            {"id": "swot_risk", "name": "SWOT Matrix and Risk Score Calculation", "status": "pending"},
            {"id": "mvp_recommendation", "name": "MVP Feature Scoping and Tech Stack", "status": "pending"},
            {"id": "gtm_strategy", "name": "Go-To-Market and Pricing Channels", "status": "pending"},
            {"id": "final_report", "name": "Executive Validation Report Synthesis", "status": "pending"}
        ]

    def update_step(self, step_id: str, status: str, details: str = "") -> None:
        for s in self.steps:
            if s["id"] == step_id:
                s["status"] = status
                if details:
                    s["details"] = details
                logger.info(f"Pipeline Step [{step_id}] -> {status}: {details}")

    def get_progress(self) -> List[Dict[str, Any]]:
        return self.steps
