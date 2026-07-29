import sys
import os
import traceback

root_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, root_dir)

try:
    from app.orchestrator import ApplicationOrchestrator
    print("SUCCESS: ApplicationOrchestrator imported successfully!")
except Exception as e:
    print("EXCEPTIONAL ERROR ENCOUNTERED:")
    traceback.print_exc()
