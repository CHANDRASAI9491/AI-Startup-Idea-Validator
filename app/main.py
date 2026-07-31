import argparse
import sys
import logging
from app.orchestrator import ApplicationOrchestrator

# Ensure UTF-8 stdout formatting on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

orchestrator = ApplicationOrchestrator()


def run_cli():
    parser = argparse.ArgumentParser(description="AI Startup Idea Validator CLI Runner")
    parser.add_argument("--idea", type=str, required=True, help="Description of the startup idea")
    parser.add_argument("--industry", type=str, default="Technology", help="Target industry sector")
    parser.add_argument("--audience", type=str, default="General Users / Businesses", help="Target audience")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("AI STARTUP IDEA VALIDATOR - CLI RUNNER")
    print("=" * 70)
    print(f"Idea: {args.idea}")
    print(f"Industry: {args.industry}")
    print("-" * 70)

    def print_progress(step, status):
        print(f"  [{step.replace('_', ' ').title()}]: {status.upper()}")

    state = orchestrator.validate_idea(
        idea_text=args.idea,
        target_industry=args.industry,
        target_audience=args.audience,
        progress_callback=print_progress
    )

    if state.final_report:
        report = state.final_report
        print("\n" + "=" * 70)
        print("VALIDATION RESULTS")
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
        print(f"\nValidation encountered an error: {state.error}\n")


if __name__ == "__main__":
    run_cli()
