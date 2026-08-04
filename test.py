import os
import sys

# Ensure root dir in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.orchestrator import ApplicationOrchestrator

def main():
    print("=== Starting End-to-End Validation Verification ===")
    orchestrator = ApplicationOrchestrator()

    idea_text = "AI-powered automated contract review and risk analysis platform for small law firms"
    print(f"Validating Idea: '{idea_text}'...")

    state = orchestrator.validate_idea(
        idea_text=idea_text,
        target_industry="Cybersecurity & Data Privacy",
        target_audience="Small Law Firms",
        business_model="B2B SaaS / Monthly Subscription",
        session_id="e2e_verification_test"
    )

    print(f"\n[Validation Status]: {state.status}")
    assert state.status == "completed", "State status should be completed!"
    assert state.final_report is not None, "Final report should not be None!"

    report = state.final_report
    scoring = report.scoring_breakdown

    print(f"[Overall Viability Score]: {report.overall_viability_score}/100")
    print(f"[Strategic Verdict]: {report.verdict}")
    print(f"[Investor Readiness Score]: {report.investor_readiness_score}/100")
    print(f"[Funding Probability]: {report.funding_probability}%")
    print(f"[Product-Market Fit Score]: {report.pmf_score}/100")

    if scoring:
        print("\n--- 8-Dimension Weighted Score Matrix ---")
        print(f"• Market Opportunity: {scoring.market_opportunity_score}/20")
        print(f"• Innovation & Differentiation: {scoring.innovation_score}/15")
        print(f"• Competition & Defensible Moat: {scoring.competition_score}/15")
        print(f"• Scalability Potential: {scoring.scalability_score}/15")
        print(f"• Technical Feasibility: {scoring.technical_feasibility_score}/10")
        print(f"• Revenue Model Viability: {scoring.revenue_model_score}/10")
        print(f"• Execution & Risk Resilience: {scoring.execution_risk_score}/10")
        print(f"• Market Timing: {scoring.market_timing_score}/5")

    print("\n--- Testing Grounded AI Advisor Q&A ---")
    question = "What is the primary customer acquisition strategy?"
    answer = orchestrator.ask_advisor("e2e_verification_test", question, [])
    print(f"Q: {question}")
    print(f"A: {answer[:250]}...")

    print("\n=== All End-to-End Verification Checks Passed Successfully! ===")

if __name__ == "__main__":
    main()