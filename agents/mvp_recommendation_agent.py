import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, MVPRecommendation, MVPFeature
from pipeline.context_passer import ContextPasser
from services.logger import get_logger

logger = get_logger(__name__)


class MVPRecommendationAgent(BaseAgent):
    """MVP Recommendation Agent scoping UVP, tech stack, feature breakdown, and 4-week roadmap."""

    def execute(self, state: StartupState) -> StartupState:
        logger.info(f"MVPRecommendationAgent scoping MVP for idea: '{state.idea.idea_text}'")
        try:
            context_summary = ContextPasser.extract_summary(state)

            prompt = self.load_prompt(
                "mvp_agent",
                idea_text=state.idea.idea_text,
                budget=state.idea.budget or "Bootstrap ($5k - $50k)",
                timeline=state.idea.timeline or "3 Months",
                context_summary=context_summary
            )

            json_data = self.generate_json(
                prompt,
                system_instruction="You are a Principal Product Architect and Fractional CTO."
            )

            if json_data:
                try:
                    state.mvp_recommendation = MVPRecommendation.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"MVPRecommendation parsing error: {e}")

            # Fallback heuristic calculation if LLM output unavailable or invalid
            state.mvp_recommendation = MVPRecommendation(
                core_value_proposition=f"Automated AI validation engine delivering investor-grade evidence for '{state.idea.idea_text}'.",
                tech_stack_frontend="Streamlit / Modern CSS Design System",
                tech_stack_backend="Python 3.11+ / LangGraph",
                tech_stack_database="PostgreSQL / SQLite Memory",
                tech_stack_ai="Google Gemini 2.5 Flash / Tavily Search API",
                features=[
                    MVPFeature(
                        feature_name="Concept & Industry Form Input",
                        priority="Must Have",
                        estimated_days=3,
                        description="Intuitive form interface supporting industry, target customer, and budget settings."
                    ),
                    MVPFeature(
                        feature_name="Multi-Agent LangGraph Pipeline",
                        priority="Must Have",
                        estimated_days=7,
                        description="7-node graph workflow coordinating research, market analysis, and risk severity scoring."
                    ),
                    MVPFeature(
                        feature_name="Deterministic Scoring Engine",
                        priority="Must Have",
                        estimated_days=4,
                        description="8-dimension viability matrix with explainable reasoning points."
                    ),
                    MVPFeature(
                        feature_name="Plotly Dashboard & Report Exporter",
                        priority="Should Have",
                        estimated_days=5,
                        description="Interactive radar/gauge charts, PDF export, and grounded AI Advisor."
                    )
                ],
                four_week_roadmap={
                    "Week 1": "Core architecture, schema models, and Tavily Search integration",
                    "Week 2": "LangGraph multi-agent pipeline & deterministic scoring engine",
                    "Week 3": "Streamlit SaaS UI design system & Plotly charts",
                    "Week 4": "Multi-format PDF/MD export, grounded Q&A advisor, & user testing"
                },
                key_metrics_kpis=[
                    "Report Generation Completion Rate (%)",
                    "Time-to-Report (< 30 seconds)",
                    "Advisor Q&A Session Engagement"
                ]
            )
        except Exception as e:
            logger.error(f"Error in MVPRecommendationAgent: {e}")
            state.error = f"MVPRecommendationAgent error: {str(e)}"
        return state
