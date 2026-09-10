# Testing & Quality Verification Guide

This document records the testing commands, test coverage structure, and known non-blocking dependency warnings for the AI Startup Idea Validator codebase.

---

## 1. Test Execution Commands

To run the complete automated test suite:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

To run a specific module or test file:

```powershell
# Run only scoring engine unit tests
.venv\Scripts\python.exe -m pytest tests/test_scoring.py

# Run only agent tests
.venv\Scripts\python.exe -m pytest tests/test_agents.py

# Run only orchestrator tests
.venv\Scripts\python.exe -m pytest tests/test_orchestrator.py
```

---

## 2. Test Suite Coverage & Verification Results

The automated test suite comprises **66 comprehensive unit and integration tests** validating:

1. **Deterministic Scoring Engine (`tests/test_scoring.py`)**:
   - Boundary checks for all 8 dimensions (0 to max points).
   - Total score calculation and ceiling clamp (0 to 100).
   - Strategic verdict mapping (`PROCEED`, `PIVOT`, `CAUTION`, `STOP`).
   - Consistency of deterministic seed offsets.
2. **State & Schema Serialization (`tests/test_schema.py`)**:
   - Pydantic V2 model validation and serialization for all domain entities.
   - Null-safety fallbacks for missing state attributes.
3. **Agent & Pipeline Execution (`tests/test_agents.py` & `tests/test_orchestrator.py`)**:
   - Prompt loading and prompt parameter substitution.
   - Deep Agents orchestrator flow and stage callback propagation (`planner`, `web_search`, `market_analysis`, `competitor_analysis`, `swot_risk`, `mvp_recommendation`, `gtm_strategy`, `report`).
   - Tavily search tool error handling and fallback mocking.
4. **Advisory & Storage (`tests/test_advisor.py` & `tests/test_storage.py`)**:
   - SQLite conversation creation, message saving, retrieval, and deletion.
   - MemoryStore caching and session lookup.
   - Intent classification heuristics and query routing.

**Latest Test Execution Summary**:
- **Result**: `66 passed in 389.59s`
- **Pass Rate**: `100%`

---

## 3. UI Component Syntax Compilation

All Streamlit frontend components are verified for Python syntax integrity using `py_compile`:

```powershell
Get-ChildItem ui\components\*.py | ForEach-Object {
    .venv\Scripts\python.exe -m py_compile $_.FullName
}
```

---

## 4. Known Non-Blocking Warnings

During test runs or application startup, you may observe the following harmless deprecation notices:
- **Pydantic V2 Config Deprecation**: Third-party dependencies (such as certain LangChain or Google GenAI integration packages) may reference `Config` or `dict()` instead of `model_config` and `model_dump()`. These warnings are upstream in external packages and do not impact project execution or scoring accuracy.
- **Tavily / Gemini Fallback in Local Mode**: If `GEMINI_API_KEY` or `TAVILY_API_KEY` are not set in the local `.env` file, the pipeline automatically operates in resilient fallback state mapping mode with informative warnings logged to `logs/`.
