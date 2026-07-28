import logging
from agents.base_agent import BaseAgent
from state.schema import StartupIdea, MVPRecommendation, MVPFeature

logger = logging.getLogger(__name__)


class MVPRecommendationAgent(BaseAgent):

    def run(self, idea: StartupIdea) -> MVPRecommendation:
        prompt = f"""
Design an MVP (Minimum Viable Product) specification for this startup concept.

Startup Idea: {idea.idea_text}
Budget: {idea.budget}
Timeline: {idea.timeline}

Respond ONLY with a JSON object matching this structure:
{{
  "core_value_proposition": "Automated, instant validation of startup ideas with real-time web insights.",
  "tech_stack_frontend": "Next.js / React / TailwindCSS",
  "tech_stack_backend": "FastAPI (Python)",
  "tech_stack_database": "PostgreSQL / Redis",
  "tech_stack_ai": "Google Gemini 2.5 API",
  "features": [
    {{
      "feature_name": "User Idea Input & Configuration",
      "priority": "Must Have",
      "estimated_days": 3,
      "description": "Simple form to specify startup title, domain, target market."
    }},
    {{
      "feature_name": "Automated Research Execution Engine",
      "priority": "Must Have",
      "estimated_days": 5,
      "description": "Multi-agent pipeline running market & competitor research."
    }},
    {{
      "feature_name": "Interactive Dashboard & PDF Export",
      "priority": "Should Have",
      "estimated_days": 4,
      "description": "Visualizing charts, SWOT matrix, and downloadable reports."
    }}
  ],
  "four_week_roadmap": {{
    "Week 1": "Core architecture, API schemas, and data model setup",
    "Week 2": "Multi-agent web search & LLM prompt integration",
    "Week 3": "Frontend dashboard & state persistence implementation",
    "Week 4": "End-to-end QA testing, beta user feedback & deployment"
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
                return MVPRecommendation.model_validate(json_data)
            except Exception as e:
                logger.warning(f"MVPRecommendation parsing error: {e}")

        # Fallback MVP recommendation
        return MVPRecommendation(
            core_value_proposition=f"Deliver fast, automated value for {idea.target_audience} looking for {idea.idea_text}.",
            tech_stack_frontend="Streamlit / React",
            tech_stack_backend="FastAPI (Python 3.11+)",
            tech_stack_database="SQLite / PostgreSQL",
            tech_stack_ai="Google Gemini API",
            features=[
                MVPFeature(
                    feature_name="Core User Request Form",
                    priority="Must Have",
                    estimated_days=2,
                    description="Input startup idea parameters and options."
                ),
                MVPFeature(
                    feature_name="Multi-Agent Analysis Engine",
                    priority="Must Have",
                    estimated_days=5,
                    description="Executes web research and LLM market synthesis."
                ),
                MVPFeature(
                    feature_name="Executive Report Export",
                    priority="Should Have",
                    estimated_days=3,
                    description="Allows founders to download Markdown and JSON reports."
                )
            ],
            four_week_roadmap={
                "Week 1": "Setup repository structure, Pydantic schemas, and API keys",
                "Week 2": "Implement multi-agent research tools and LLM prompt templates",
                "Week 3": "Develop Streamlit UI & FastAPI server endpoints",
                "Week 4": "Run user testing, refine scoring algorithms, and launch"
            },
            key_metrics_kpis=[
                "Validation Completion Rate (>90%)",
                "Average Validation Duration (<45s)",
                "User Recommendation Rate (>80%)"
            ]
        )
