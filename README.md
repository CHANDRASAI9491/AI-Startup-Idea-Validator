# AI Startup Idea Validator

A production-grade, multi-agent AI system that evaluates, scores, and generates strategic validation reports for early-stage startup concepts.

## 🚀 Features

- **Multi-Agent DAG Architecture**:
  - 🔍 **Web Search Agent**: Gathers live web data, market news, competitors, and pain points via DuckDuckGo.
  - 📈 **Market Analysis Agent**: Computes TAM/SAM/SOM market sizing, CAGR %, growth drivers, and target personas.
  - ⚔️ **Competitor Agent**: Identifies direct/indirect competitors, feature trade-offs, and competitive moats.
  - 🛡️ **SWOT & Risk Agent**: Assesses Strengths, Weaknesses, Opportunities, Threats, and risk scores (1-10).
  - 🛠️ **MVP Recommendation Agent**: Scopes core features (Must/Should Have), recommended tech stack, and 4-week roadmap.
  - 🎯 **Go-To-Market Agent**: Formulates customer acquisition channels, pricing model, and launch tactics.
  - 📊 **Validation Report Agent**: Synthesizes a 0-100 Viability Index and executive verdict (`PROCEED`, `PIVOT`, `CAUTION`, `STOP`).
  - 💬 **Interactive AI Advisor**: Real-time Q&A assistant grounded in validation report findings.

## 🛠️ Technology Stack

- **Core**: Python 3.11+
- **LLM Engine**: Google Gemini API (`google-genai`) with fallback heuristics
- **Data & Validation**: Pydantic v2
- **Search Tool**: DuckDuckGo Search (`ddgs`)
- **Web UI**: Streamlit
- **REST API**: FastAPI + Uvicorn
- **Testing**: Pytest

---

## 🏃 How to Run

### 1. Interactive Web Application (Streamlit UI)
```bash
.\.venv\Scripts\python.exe -m streamlit run ui/streamlit_app.py
```
Open [http://localhost:8501](http://localhost:8501) in your web browser.

### 2. Command Line Interface (CLI)
```bash
.\.venv\Scripts\python.exe -m app.main --idea "AI-powered B2B platform for automated financial auditing" --industry "FinTech"
```

### 3. REST API Web Server (FastAPI)
```bash
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
API Documentation available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 4. Run Test Suite
```bash
.\.venv\Scripts\python.exe -m pytest -v
```
