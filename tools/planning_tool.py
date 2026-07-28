import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class PlanningTool:
    """Tracks task planning and execution steps for multi-agent validation."""

    def __init__(self):
        self.steps = [
            {"id": "web_search", "name": "Web Research & Market Data Gathering", "status": "pending"},
            {"id": "market_analysis", "name": "TAM/SAM/SOM & Market Size Evaluation", "status": "pending"},
            {"id": "competitor_analysis", "name": "Competitive Matrix & Moat Mapping", "status": "pending"},
            {"id": "swot_risk", "name": "SWOT Matrix & Risk Score Calculation", "status": "pending"},
            {"id": "mvp_recommendation", "name": "MVP Feature Scoping & Tech Stack", "status": "pending"},
            {"id": "gtm_strategy", "name": "Go-To-Market & Pricing Channels", "status": "pending"},
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
