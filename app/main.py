import argparse
import json
import logging
import sys
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.orchestrator import ApplicationOrchestrator

# Ensure UTF-8 stdout formatting on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# FastAPI Application Instance
app = FastAPI(
    title="AI Startup Idea Validator API",
    description="Multi-Agent System for validating, scoring, and providing strategic insights for startup concepts.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = ApplicationOrchestrator()


class ValidateRequest(BaseModel):
    idea_text: str
    target_industry: Optional[str] = "Technology"
    target_audience: Optional[str] = "General Users / Businesses"
    budget: Optional[str] = "Bootstrap ($5k - $50k)"
    timeline: Optional[str] = "3 Months"
    session_id: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []


@app.get("/")
def read_root():
    return {
        "service": "AI Startup Idea Validator",
        "status": "online",
        "endpoints": ["/api/validate", "/api/history", "/api/report/{session_id}", "/api/advisor/chat"]
    }


@app.post("/api/validate")
def validate_idea_endpoint(req: ValidateRequest):
    try:
        state = orchestrator.validate_idea(
            idea_text=req.idea_text,
            target_industry=req.target_industry,
            target_audience=req.target_audience,
            budget=req.budget,
            timeline=req.timeline,
            session_id=req.session_id
        )
        return {
            "status": "success",
            "session_id": req.session_id,
            "overall_score": state.final_report.overall_viability_score if state.final_report else None,
            "verdict": state.final_report.verdict if state.final_report else None,
            "report": state.final_report,
            "state": state
        }
    except Exception as e:
        logger.exception("Validation error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
def get_history():
    return {"sessions": orchestrator.list_all_sessions()}


@app.get("/api/report/{session_id}")
def get_report(session_id: str):
    state = orchestrator.get_session_history(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return state


@app.post("/api/advisor/chat")
def chat_with_advisor(req: ChatRequest):
    answer = orchestrator.ask_advisor(req.session_id, req.question, req.chat_history or [])
    return {"answer": answer}


def run_cli():
    parser = argparse.ArgumentParser(description="AI Startup Idea Validator CLI")
    parser.add_argument("--idea", type=str, required=True, help="Description of the startup idea")
    parser.add_argument("--industry", type=str, default="Technology", help="Target industry sector")
    parser.add_argument("--audience", type=str, default="General Users / Businesses", help="Target audience")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("[*] AI STARTUP IDEA VALIDATOR - CLI RUNNER")
    print("=" * 70)
    print(f"Idea: {args.idea}")
    print(f"Industry: {args.industry}")
    print("-" * 70)

    def print_progress(step, status):
        print(f"  [+] {step.replace('_', ' ').title()}: {status.upper()}")

    state = orchestrator.validate_idea(
        idea_text=args.idea,
        target_industry=args.industry,
        target_audience=args.audience,
        progress_callback=print_progress
    )

    if state.final_report:
        report = state.final_report
        print("\n" + "=" * 70)
        print("[RESULTS] VALIDATION RESULTS")
        print("=" * 70)
        print(f"Overall Viability Score: {report.overall_viability_score}/100")
        print(f"Verdict: {report.verdict}")
        print("\nExecutive Summary:")
        print(report.executive_summary)
        print("\nKey Takeaways:")
        for t in report.key_takeaways:
            print(f" - {t}")
        print("\nRecommended Next Steps:")
        for i, step in enumerate(report.recommended_next_steps, 1):
            print(f" {i}. {step}")
        print("=" * 70 + "\n")
    else:
        print(f"\n[ERROR] Validation encountered an error: {state.error}\n")


if __name__ == "__main__":
    run_cli()
