# AI Startup Idea Validator

An enterprise-grade, hybrid AI decision support platform that analyzes startup concepts and produces evidence-driven validation reports using Google Gemini 2.5 Flash, DeepAgents Planner, LangGraph StateGraph, and Streamlit.

The system performs deep market research, TAM/SAM/SOM sizing, competitive intelligence, SWOT matrix mapping, risk probability & impact calculation, MVP scoping, and go-to-market strategy formulation. It calculates a deterministic 8-dimension weighted viability score (out of 100) and investor readiness metrics instead of relying on random LLM guesses.

---

## Overview

The **AI Startup Idea Validator** assists entrepreneurs, venture capital analysts, and product managers in evaluating startup concepts before allocating capital and development resources.

Instead of generic AI text generation or manual web searches, this platform combines a **Deterministic Hybrid Scoring Engine** with live DuckDuckGo market search and a multi-agent LangGraph workflow to produce explainable, evidence-backed evaluation reports.

---

## Key Features

- **Multi-Agent Orchestration**: DeepAgents Strategic Planner + 8 LangGraph Agent Nodes.
- **Deterministic Scoring Engine**: 8-dimension weighted score matrix (out of 100) with explainable reasoning ("WHY").
- **Investor Decision Metrics**: Investor Readiness Score, Funding Probability %, Product-Market Fit Score, Innovation Index, and Complexity Indices.
- **Live Web Research**: Deduplicated, source-ranked search using DuckDuckGo.
- **Quantitative Market Sizing**: TAM, SAM, SOM volume calculations and 5-year CAGR growth projections.
- **Risk Severity Matrix**: Categorized risk assessment evaluating Probability (1-5) x Impact (1-5).
- **MVP & GTM Blueprints**: Feature prioritization (Must/Should/Nice to Have), 4-week development roadmap, and customer acquisition channels.
- **Rich Plotly Visualizations**: Viability Gauge, 8-Dimension Matrix Bar Chart, 5-Year Market Line Chart, SWOT Radar, and Risk Pie Chart.
- **Multi-Format Exports**: PDF (ReportLab), Markdown, and JSON state file downloads.
- **Conversational AI Advisor**: Grounded Q&A chatbot answering follow-up questions exclusively from report context.
- **Pure Streamlit Architecture**: Pure in-memory invocation without REST API overhead.

---

## Multi-Agent Workflow

```text
User Startup Concept Description
        │
        ▼
DeepAgents Strategic Planner
        │
        ▼
Web Search Agent (DuckDuckGo Snippets)
        │
        ▼
Market Analysis Agent (TAM / SAM / SOM & CAGR)
        │
        ▼
Competitor Analysis Agent (Matrix & Moat Mapping)
        │
        ▼
SWOT & Risk Agent (Probability x Impact Severity Matrix)
        │
        ▼
MVP Recommendation Agent (Roadmap & Tech Stack)
        │
        ▼
Go-To-Market Agent (Channels & Pricing Strategy)
        │
        ▼
Deterministic Hybrid Scoring Engine (8-Dimension Matrix)
        │
        ▼
Report Agent (Investor Synthesis)
        │
        ▼
Interactive AI Advisor (Grounded Q&A)
        │
        ▼
Final Validation Report (PDF / MD / JSON)
```

---

## Technology Stack

- **Core Engine**: Python 3.11+
- **AI Framework**: LangChain, LangGraph, DeepAgents Planner
- **LLM Engine**: Google Gemini 2.5 Flash
- **Web Search**: DuckDuckGo Search API
- **State & Schema Validation**: Pydantic 2.0+
- **User Interface**: Streamlit with custom CSS gradient styling
- **Data Visualizations**: Plotly (Gauge, Bar, Line, Radar, Pie)
- **Document Generation**: ReportLab (PDF) & Markdown
- **Automated Testing**: Pytest

---

## Project Structure

```text
AI-Startup-Idea-Validator/

├── agents/                 # Multi-agent implementations
│   ├── base_agent.py
│   ├── web_search_agent.py
│   ├── market_analysis_agent.py
│   ├── competitor_agent.py
│   ├── swot_risk_agent.py
│   ├── mvp_recommendation_agent.py
│   ├── gtm_strategy_agent.py
│   ├── report_agent.py
│   └── conversational_advisor.py
├── app/                    # Configuration and Application Orchestrator
│   ├── config.py
│   ├── main.py
│   └── orchestrator.py
├── pipeline/               # LangGraph StateGraph workflow definition
│   └── graph.py
├── services/               # Deterministic Hybrid Scoring Engine & Gemini LLM service
│   ├── llm_service.py
│   └── scoring_engine.py
├── state/                  # Pydantic schemas and in-memory state store
│   ├── memory.py
│   └── schema.py
├── tools/                  # Search, planning, and PDF/Markdown file export tools
│   ├── file_tools.py
│   ├── planning_tool.py
│   └── search_tool.py
├── ui/                     # Modular Streamlit UI components
│   ├── streamlit_app.py
│   └── components/
│       ├── advisor.py
│       ├── cards.py
│       ├── charts.py
│       ├── footer.py
│       ├── forms.py
│       ├── header.py
│       ├── navbar.py
│       ├── progress.py
│       ├── report.py
│       ├── sidebar.py
│       ├── styles.py
│       └── theme.py
├── tests/                  # Pytest unit and end-to-end test suite
├── reports/                # Generated validation output files
├── requirements.txt
└── README.md
```

---

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/CHANDRASAI9491/AI-Startup-Idea-Validator.git
   cd AI-Startup-Idea-Validator
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
   MODEL_NAME=gemini-2.5-flash
   ENABLE_WEB_SEARCH=true
   MAX_SEARCH_RESULTS=5
   EXPORT_DIR=reports
   ```

---

## Running the Application

Launch the Streamlit web application:

```bash
streamlit run ui/streamlit_app.py
```

---

## Running Automated Tests

Run the full Pytest test suite:

```bash
pytest tests -v
```

---

## License

This project is licensed under the MIT License.
