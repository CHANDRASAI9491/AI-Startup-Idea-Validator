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
.venv\Scripts\python.exe -m pytest tests/test_scoring_engine.py

# Run only agent tests
.venv\Scripts\python.exe -m pytest tests/test_market_agent.py tests/test_competitor_agent.py

# Run only integration and pipeline tests
.venv\Scripts\python.exe -m pytest tests/test_deep_agents_integration.py tests/test_pipeline_e2e.py
```

---

## 2. Test Suite Coverage & Verification Results

The automated test suite comprises **177 comprehensive automated unit and integration tests** validating:

1. **Deterministic Scoring Engine (`tests/test_scoring_engine.py`)**:
   - Boundary checks for all 8 dimensions (0 to max points).
   - Total score calculation and ceiling clamp (0 to 100).
   - Strategic verdict mapping (`PROCEED`, `CAUTION`, `PIVOT`, `STOP`).
   - Scoring determinism and punctuation invariance (no hash/seed pseudo-variance).
   - Missing market evidence handling (unweighted baseline and limitation reporting).
   - Missing competitor evidence handling and verified zero competitor handling.
   - Score explainability and evidence limitation generation ("Why This Score?").
2. **Search Services & Evidence Provenance (`tests/test_web_search.py`, `tests/test_retrieval_utils.py`)**:
   - Real research retrieval preserving title, URL, snippet, query, category, and ISO UTC timestamp.
   - Prevention of fabricated Tavily fallback data; honest empty-result handling.
   - Preservation of source URLs in prompt context formatting without synthetic placeholder domains.
3. **Multi-Agent Pipeline Execution & Analysis (`tests/test_deep_agents_*.py`, `tests/test_*_agent.py`, `tests/test_pipeline_e2e.py`)**:
   - Market and competitor analysis parsing of real evidence and honest fallback when evidence is unavailable.
   - Deep Agents orchestrator flow, callback propagation, and Pydantic state population.
   - Unsupported-value prevention (no invented TAM, SAM, SOM, CAGR, or placeholder competitors).
   - Grounded report generation with missing-evidence handling.
   - Free-Tier optimizations: deterministic planning (`use_llm=False`), `max_retries=0`, `recursion_limit=10`, no redundant subagent tools.
4. **Conversational Advisory & Storage (`tests/test_conversational_advisor.py`, `tests/test_chat_history.py`)**:
   - Intent classification heuristics, multi-turn follow-up inheritance, and grounded report context.
   - Advisor missing-value handling (avoidance of `$NoneB` or `None%`).
   - SQLite conversation creation, message saving, retrieval, session isolation, and cascade deletion.

**Latest Test Execution Summary**:

- **Result**: `177 passed, 0 failed, 1 warning`
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

During test runs or application startup, you may observe the following harmless deprecation notice:

- **Python 3.14 / google.genai `_UnionGenericAlias` Warning**: Under Python 3.14 environments, `google/genai/types.py` produces a non-fatal `DeprecationWarning: '_UnionGenericAlias' is deprecated and slated for removal in Python 3.17`. This is an upstream SDK typing notification that does not affect runtime execution, deterministic scoring, or test results.
- **Tavily / Gemini Fallback in Local Mode**: If `GEMINI_API_KEY` or `TAVILY_API_KEY` are not set in the local `.env` file, the pipeline automatically operates in resilient fallback state mapping mode with informative warnings logged to `logs/`.
