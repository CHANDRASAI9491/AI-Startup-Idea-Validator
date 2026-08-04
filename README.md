# AI Startup Idea Validator

## Overview

AI Startup Idea Validator is a multi-agent AI application that evaluates startup ideas using LangGraph, Google Gemini, Tavily Search, and a deterministic scoring engine. The system performs real-time market research, competitor analysis, SWOT analysis, MVP planning, Go-To-Market strategy generation, and produces a comprehensive startup validation report with an overall viability score.

The project is designed to help entrepreneurs, students, startup founders, incubators, and innovation teams validate business ideas before investing significant time and resources.

---

## Key Features

- Multi-Agent AI Workflow using LangGraph
- Real-Time Market Research using Tavily Search
- Google Gemini Integration for AI Reasoning
- Startup Planning Agent
- Market Analysis
- Competitor Analysis
- SWOT & Risk Assessment
- MVP Recommendation Generation
- Go-To-Market Strategy Generation
- Deterministic Startup Viability Scoring
- Professional Interactive Streamlit Dashboard
- Interactive AI Advisor
- Export Reports in PDF, Markdown, and JSON formats

---

## Technology Stack

### Frontend

- Streamlit
- HTML
- CSS
- Plotly

### Backend

- Python 3.11
- LangGraph
- Google Gemini
- Tavily Search API
- Pydantic
- Deterministic Scoring Engine

---

## Project Structure

```text
AI-Startup-Idea-Validator/
│
├── agents/
│   ├── web_search_agent.py
│   ├── market_analysis_agent.py
│   ├── competitor_agent.py
│   ├── swot_risk_agent.py
│   ├── mvp_recommendation_agent.py
│   ├── gtm_strategy_agent.py
│   ├── report_agent.py
│   └── conversational_advisor.py
│
├── app/
│   ├── config.py
│   ├── orchestrator.py
│   └── main.py
│
├── pipeline/
│   └── graph.py
│
├── prompts/
│
├── reports/
│
├── services/
│
├── state/
│
├── tools/
│
├── ui/
│   ├── streamlit_app.py
│   └── components/
│
├── tests/
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## System Workflow

1. User enters a startup idea.
2. Planner Agent creates an execution strategy.
3. Tavily Search gathers live market intelligence.
4. Market Analysis Agent evaluates market opportunity.
5. Competitor Agent identifies existing competitors.
6. SWOT Agent performs business risk analysis.
7. MVP Agent recommends product features and roadmap.
8. GTM Agent generates launch and marketing strategies.
9. Report Agent prepares the final validation report.
10. Interactive AI Advisor answers follow-up questions.
11. Results are displayed through the Streamlit dashboard.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/CHANDRASAI9491/AI-Startup-Idea-Validator.git

cd AI-Startup-Idea-Validator
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY

TAVILY_API_KEY=YOUR_TAVILY_API_KEY

MODEL_NAME=gemini-2.5-flash-lite

MAX_SEARCH_RESULTS=5

EXPORT_DIR=reports
```

---

## Running the Application

Launch the Streamlit application:

```bash
python -m streamlit run ui/streamlit_app.py
```

Open the application in your browser:

```
http://localhost:8501
```

---

## Example Startup Description

```
An AI-powered healthcare platform that helps hospitals and clinics automate patient appointment scheduling, symptom assessment, electronic medical record summarization, doctor recommendations, and hospital resource management. Patients interact with an AI assistant to book appointments, receive personalized healthcare guidance, and access medical records. Doctors receive AI-generated patient summaries before consultations while hospital administrators monitor operational efficiency using intelligent analytics dashboards.
```

---

## Testing

Run the complete test suite:

```bash
pytest tests -v
```

---

## Example Output

The system generates:

- Executive Summary
- Market Opportunity Analysis
- Customer Pain Points
- Competitor Analysis
- SWOT Analysis
- Risk Assessment
- MVP Roadmap
- Go-To-Market Strategy
- Startup Viability Score
- Final Recommendation
- Exportable PDF, Markdown, and JSON reports

---

## Current Capabilities

- AI Startup Validation
- Multi-Agent Workflow
- Live Web Research
- Market Trend Analysis
- Competitor Intelligence
- SWOT & Risk Assessment
- MVP Planning
- Go-To-Market Strategy
- Deterministic Startup Scoring
- Interactive Dashboard
- Professional Charts & Visualizations
- AI-Powered Business Insights

---

## Future Enhancements

- Investor Pitch Deck Generator
- Financial Forecasting
- Startup Comparison Dashboard
- User Authentication
- Cloud Deployment
- Multi-Language Support
- Startup Portfolio Management

---

## Team

**Team Lead**

- Pothuri Chandra Sai

**Team Members**

- Yashika Chaudary
- Harsha
- Karthik

---


## License

This project is developed for educational and research purposes.
