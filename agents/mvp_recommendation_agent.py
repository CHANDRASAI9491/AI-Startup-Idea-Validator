import logging
from agents.base_agent import BaseAgent
from state.schema import StartupState, MVPRecommendation, MVPFeature

logger = logging.getLogger(__name__)


class MVPRecommendationAgent(BaseAgent):
    """MVP Recommendation Agent defining value prop, tech stack, feature roadmap, and KPIs."""

    def run(self, state: StartupState) -> StartupState:
        logger.info(f"MVPRecommendationAgent running for idea: {state.idea.idea_text}")
        try:
            prompt = f"""
Design an MVP (Minimum Viable Product) specification for this startup concept.

Startup Idea: {state.idea.idea_text}
Industry: {state.idea.target_industry}
Budget: {state.idea.budget}
Timeline: {state.idea.timeline}

Respond ONLY with a JSON object matching this structure:
{{
  "core_value_proposition": "Automated, instant validation of startup ideas with real-time web insights.",
  "tech_stack_frontend": "Streamlit / Next.js",
  "tech_stack_backend": "FastAPI (Python 3.12+)",
  "tech_stack_database": "PostgreSQL / SQLite",
  "tech_stack_ai": "Google Gemini 2.5 Flash API",
  "features": [
    {{
      "feature_name": "User Idea Input & Configuration",
      "priority": "Must Have",
      "estimated_days": 3,
      "description": "Form inputs capturing idea, industry, audience, budget, timeline."
    }},
    {{
      "feature_name": "Automated Research Execution Engine",
      "priority": "Must Have",
      "estimated_days": 5,
      "description": "Multi-agent pipeline running market and competitor research."
    }},
    {{
      "feature_name": "Interactive Dashboard and Report Export",
      "priority": "Should Have",
      "estimated_days": 4,
      "description": "Visualizing charts, SWOT matrix, and downloadable reports."
    }}
  ],
  "four_week_roadmap": {{
    "Week 1": "Core architecture, API schemas, and data model setup",
    "Week 2": "Multi-agent web search and LLM prompt integration",
    "Week 3": "Frontend dashboard and state persistence implementation",
    "Week 4": "End-to-end QA testing, beta user feedback and deployment"
  }},
  "key_metrics_kpis": [
    "MVP User Conversion Rate (>15%)",
    "Report Generation Time (<30 seconds)",
    "User Satisfaction / Net Promoter Score (>50)"
  ]
}}
"""
            json_data = self.generate_json(prompt, system_instruction="You are a Technical Product Manager.")

            if json_data:
                try:
                    state.mvp_recommendation = MVPRecommendation.model_validate(json_data)
                    return state
                except Exception as e:
                    logger.warning(f"MVPRecommendation parsing error: {e}")

            # Fallback MVP recommendation if LLM output unavailable or invalid
            state.mvp_recommendation = MVPRecommendation(
                core_value_proposition=f"Deliver instant automated value for {state.idea.target_audience} solving {state.idea.idea_text}.",
                tech_stack_frontend="Streamlit / React",
                tech_stack_backend="FastAPI (Python 3.12+)",
                tech_stack_database="SQLite / PostgreSQL",
                tech_stack_ai="Google Gemini 2.5 Flash",
                features=[
                    MVPFeature(
                        feature_name="Core Idea Form and Parameters",
                        priority="Must Have",
                        estimated_days=2,
                        description="Input form capturing concept description, audience, and budget."
                    ),
                    MVPFeature(
                        feature_name="Multi-Agent Validation Engine",
                        priority="Must Have",
                        estimated_days=5,
                        description="Executes web research and LLM market synthesis."
                    ),
                    MVPFeature(
                        feature_name="Executive Report Export (MD, JSON, PDF)",
                        priority="Should Have",
                        estimated_days=3,
                        description="Allows founders to download Markdown, JSON, and PDF reports."
                    )
                ],
                four_week_roadmap={
                    "Week 1": "Setup repository structure, Pydantic schemas, and API keys",
                    "Week 2": "Implement multi-agent research tools and LLM prompt templates",
                    "Week 3": "Develop Streamlit UI and backend orchestrator",
                    "Week 4": "Run user testing, refine scoring algorithms, and launch"
                },
                key_metrics_kpis=[
                    "Validation Completion Rate (>90%)",
                    "Average Validation Duration (<45s)",
                    "User Recommendation Rate (>80%)"
                ]
            )
        except Exception as e:
            logger.error(f"Error in MVPRecommendationAgent: {e}")
            state.error = f"MVPRecommendationAgent error: {str(e)}"
        return state
