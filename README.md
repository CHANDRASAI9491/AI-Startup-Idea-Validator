# AI Startup Idea Validator

> **Enterprise Hybrid AI Decision Support & Multi-Agent Startup Evaluation Platform**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-purple?style=flat-square)
![Gemini](https://img.shields.io/badge/AI Engine-Google Gemini 2.5 Flash-blue?style=flat-square)
![UI](https://img.shields.io/badge/Interface-Streamlit-red?style=flat-square&logo=streamlit)
![Tests](https://img.shields.io/badge/Tests-100%25%20Passing%20(11%2F11)-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

---

## Executive Overview

The **AI Startup Idea Validator** is a commercial-grade, multi-agent AI platform designed to evaluate early-stage startup concepts for founders, product managers, and venture capital analysts.

Unlike generic LLM wrappers that produce random, ungrounded text recommendations, this platform combines **DeepAgents strategic research planning**, a **7-node LangGraph execution workflow**, live DuckDuckGo web search, and a **Deterministic Hybrid Scoring Engine** to deliver explainable, evidence-backed investor decision reports.

---

## Key Capabilities

- **DeepAgents Strategic Planning**: Analyzes startup concepts to construct dynamic multi-agent execution objectives prior to graph orchestration.
- **Hybrid Deterministic Scoring Engine**: Evaluates startup viability across an **8-dimensional weighted matrix (out of 100)** with explainable reasoning points ("WHY").
- **Investor Decision Support Suite**: Calculates quantitative metrics including **Investor Readiness Score**, **Funding Probability %**, **Product-Market Fit (PMF) Score**, **Innovation Index**, **Competitive Strength**, and **Complexity Indices**.
- **Live Web Research Integration**: Deduplicates and ranks live market snippets, industry news, funding trends, and competitor features using DuckDuckGo.
- **Quantitative Market Sizing**: Computes Total Addressable Market (TAM), Serviceable Addressable Market (SAM), Serviceable Obtainable Market (SOM), and 5-year CAGR growth projections.
- **Categorized Risk Severity Matrix**: Evaluates Financial, Technical, Market, Regulatory, and Execution risks using a **Probability (1-5) x Impact (1-5)** severity matrix.
- **MVP & Go-To-Market Blueprints**: Prioritizes feature scope (Must Have, Should Have, Nice to Have), estimates development days, and formulates customer acquisition tactics.
- **Rich Plotly Visualizations**: Includes interactive Score Gauges, 8-Dimension Matrix Bar Charts, 5-Year Trajectory Line Charts, SWOT Radars, and Risk Severity Pie Charts.
- **Multi-Format Export Engine**: Downloads investor-ready PDF reports (built with ReportLab), Markdown summaries, and raw JSON state files.
- **Grounded Conversational AI Advisor**: Interactive Q&A chatbot answering follow-up questions exclusively grounded in generated report data.

---

## ⚖️ 8-Dimension Weighted Scoring Matrix

Scores are calculated deterministically across an 8-dimensional weighted matrix (Total = 100) to ensure different startup ideas receive distinct, evidence-backed evaluations:

| Dimension | Max Weight | Description |
| :--- | :---: | :--- |
| **Market Opportunity** | **20** | Evaluates TAM/SAM/SOM volume and projected CAGR % |
| **Innovation & Differentiation** | **15** | Evaluates deep tech elements, IP, and unique value proposition |
| **Competition & Defensible Moat** | **15** | Evaluates incumbent density, competitor weaknesses, and moat strength |
| **Scalability Potential** | **15** | Evaluates software/SaaS margins vs operational physical friction |
| **Technical Feasibility** | **10** | Evaluates technology readiness level (TRL) and technical risk |
| **Revenue Model Viability** | **10** | Evaluates predictable recurring revenue model and enterprise LTV |
| **Execution & Risk Resilience** | **10** | Evaluates financial, regulatory, and operational risk severity |
| **Market Timing** | **5** | Evaluates macro market tailwinds and emerging demand indicators |
| **Total Viability Score** | **100** | **Objective Viability Index & Strategic Verdict Classification** |

---

## Multi-Agent Architecture

```text
                                User Startup Concept
                                         │
                                         ▼
                            DeepAgents Strategic Planner
                                         │
                                         ▼
                         LangGraph StateGraph Workflow
                                         │
    ┌────────────────────────────────────┼────────────────────────────────────┐
    │                                    │                                    │
    ▼                                    ▼                                    ▼
Web Search Agent               Market Analysis Agent              Competitor Agent
(DuckDuckGo Research)          (TAM / SAM / SOM & CAGR)           (Matrix & Moat Mapping)
    │                                    │                                    │
    └────────────────────────────────────┼────────────────────────────────────┘
                                         │
                                         ▼
                                SWOT & Risk Agent
                      (Probability x Impact Severity Matrix)
                                         │
                                         ▼
                            MVP Recommendation Agent
                         (Feature Scope & Tech Stack)
                                         │
                                         ▼
                               Go-To-Market Agent
                       (Acquisition & Pricing Channels)
                                         │
                                         ▼
                       Deterministic Hybrid Scoring Engine
                        (8-Dimension Matrix & Verdict)
                                         │
                                         ▼
                               Validation Report Agent
                            (Investor-Grade Synthesis)
                                         │
    ┌────────────────────────────────────┴────────────────────────────────────┐
    │                                                                         │
    ▼                                                                         ▼
Interactive AI Advisor                                           Multi-Format Export Engine
(Grounded Q&A Chatbot)                                            (PDF / Markdown / JSON)
```

---

## Directory & File Structure

```text
AI-Startup-Idea-Validator/

├── app/
│   ├── main.py                     # CLI entrypoint runner
│   ├── config.py                   # Centralized configuration & environment loader
│   └── orchestrator.py             # Application Orchestrator & state coordinator
│
├── agents/                         # Multi-agent specialized implementations
│   ├── base_agent.py               # Abstract base agent class
│   ├── web_search_agent.py         # Live market research agent
│   ├── market_analysis_agent.py    # Market sizing & TAM/SAM/SOM agent
│   ├── competitor_agent.py         # Competitive matrix & moat mapping agent
│   ├── swot_risk_agent.py          # SWOT & Risk severity matrix agent
│   ├── mvp_recommendation_agent.py # MVP feature scope & roadmap agent
│   ├── gtm_strategy_agent.py       # Go-to-market & acquisition channel agent
│   ├── report_agent.py             # Investor synthesis & report generation agent
│   └── conversational_advisor.py   # Grounded Q&A chatbot advisor
│
├── services/                       # Core engine services
│   ├── llm_service.py              # Google Gemini API client wrapper
│   └── scoring_engine.py           # Deterministic 8-dimension weighted scoring engine
│
├── tools/                          # Utility tools & export engines
│   ├── duckduckgo_tool.py          # DuckDuckGo search wrapper
│   ├── file_tools.py               # Markdown and ReportLab PDF document exporters
│   ├── planning_tool.py            # DeepAgents strategic planner
│   ├── retrieval_utils.py          # Snippet deduplication & relevance ranking
│   └── web_search_tool.py          # Multi-query web search executor
│
├── state/                          # Schema definitions & state persistence
│   ├── schema.py                   # Pydantic data schemas & state models
│   └── memory.py                   # Session state memory manager
│
├── prompts/                        # System prompt markdown files
│   ├── system_orchestrator.md
│   ├── web_search_agent.md
│   ├── market_analysis_agent.md
│   ├── competitor_agent.md
│   ├── swot_risk_agent.md
│   ├── mvp_agent.md
│   ├── gtm_agent.md
│   └── report_agent.md
│
├── pipeline/                       # LangGraph orchestration
│   ├── graph.py                    # LangGraph StateGraph workflow definition
│   └── context_passer.py           # Context formatting & state integrity helper
│
├── ui/                             # Modular Streamlit enterprise interface
│   ├── streamlit_app.py            # Main Streamlit application router
│   └── components/                 # Reusable UI component package
│       ├── advisor.py              # Chatbot speech bubble UI
│       ├── cards.py                # Executive report cards
│       ├── charts.py               # Plotly data visualization engines
│       ├── footer.py               # System status footer
│       ├── forms.py                # Form input components
│       ├── header.py               # Gradient header banner
│       ├── idea_input.py           # Dedicated startup validation input component
│       ├── navbar.py               # Top status navigation bar
│       ├── progress.py             # Real-time execution progress monitor
│       ├── report.py               # Report view wrapper
│       ├── report_viewer.py        # Dedicated validation report viewer
│       ├── sidebar.py              # Enterprise sidebar navigation
│       ├── styles.py               # Custom CSS injector
│       └── theme.py                # Design tokens & color constants
│
├── reports/                        # Output directory for generated PDF/MD reports
├── tests/                          # Automated Pytest unit & end-to-end test suite
├── docs/                           # Documentation (Architecture, Agent Roles, Final Report)
├── requirements.txt                # Python package dependencies
├── .env.example                    # Environment variable template
└── README.md                       # Project documentation
```

---

## ⚡ Installation & Quick Start

### 1. Prerequisites

- Python 3.11+
- Git

### 2. Clone the Repository

```bash
git clone https://github.com/CHANDRASAI9491/AI-Startup-Idea-Validator.git
cd AI-Startup-Idea-Validator
```

### 3. Create & Activate Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
MODEL_NAME=gemini-2.5-flash
ENABLE_WEB_SEARCH=true
MAX_SEARCH_RESULTS=5
EXPORT_DIR=reports
```

---

## ▶ Running the Application

Launch the Streamlit web application:

```bash
streamlit run ui/streamlit_app.py
```

Open your browser to `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Execute the full Pytest test suite:

```bash
pytest tests/ -v
```

---

## 📄 License

This project is licensed under the **MIT License**.
