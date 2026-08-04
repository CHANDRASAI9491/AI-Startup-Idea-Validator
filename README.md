# AI Startup Idea Validator

## Overview

AI Startup Idea Validator is a production-ready multi-agent AI platform that helps entrepreneurs evaluate startup ideas before investing time and resources.

The system performs market research, competitor analysis, SWOT analysis, risk assessment, MVP planning, go-to-market strategy generation, and investor-oriented startup evaluation using a coordinated multi-agent workflow.

Instead of generating generic AI responses, the platform combines real-time web intelligence with deterministic scoring and structured AI reasoning to produce an evidence-based startup validation report.

---

# Key Features

- Multi-Agent AI Architecture
- DeepAgents Orchestration
- LangGraph Workflow Management
- Google Gemini Integration
- Tavily Search Integration
- Real-Time Market Research
- Competitor Analysis
- SWOT Analysis
- Risk Assessment
- MVP Recommendation
- Go-To-Market Strategy
- Deterministic Startup Scoring
- Investor Readiness Analysis
- Startup Viability Score
- AI Conversational Advisor
- Interactive Streamlit Interface
- Plotly Visualizations
- Exportable Reports

---

# System Architecture

```
User
        │
        ▼
Streamlit Application
        │
        ▼
Application Orchestrator
        │
        ▼
DeepAgents Planner
        │
        ▼
LangGraph Workflow
        │
        ├──────────────► Web Search Agent
        │
        ├──────────────► Market Analysis Agent
        │
        ├──────────────► Competitor Analysis Agent
        │
        ├──────────────► SWOT & Risk Agent
        │
        ├──────────────► MVP Recommendation Agent
        │
        ├──────────────► Go-To-Market Agent
        │
        ├──────────────► Validation Report Agent
        │
        └──────────────► Conversational Advisor
                         │
                         ▼
        Google Gemini + Tavily Search
                         │
                         ▼
            Startup Validation Report
```

---

# Technology Stack

## Language

- Python 3.11+

## Application Framework

- Streamlit

## AI Orchestration

- DeepAgents

## Workflow Engine

- LangGraph

## LLM Framework

- LangChain

## Large Language Model

- Google Gemini

## Search Engine

- Tavily Search

## Data Validation

- Pydantic

## Visualization

- Plotly

## Testing

- Pytest

---

# Project Structure

```
ai-startup-validator/

├── app/
├── agents/
├── services/
├── pipeline/
├── state/
├── tools/
├── prompts/
├── ui/
├── reports/
├── tests/
├── docs/
├── requirements.txt
├── README.md
└── .env.example
```

---

# AI Agents

### Web Search Agent

Collects live industry trends, competitors, market insights, and supporting evidence using Tavily Search.

### Market Analysis Agent

Analyzes market opportunity, customer segments, industry growth, TAM, SAM, and SOM.

### Competitor Analysis Agent

Identifies direct and indirect competitors and evaluates competitive positioning.

### SWOT & Risk Agent

Performs SWOT analysis and evaluates business, technical, financial, and operational risks.

### MVP Recommendation Agent

Generates a prioritized Minimum Viable Product roadmap.

### Go-To-Market Agent

Creates pricing strategies, customer acquisition plans, marketing channels, and launch recommendations.

### Validation Report Agent

Combines outputs from all AI agents into a structured startup validation report.

### Conversational Advisor

Allows users to ask follow-up questions based on the generated validation report.

---

# Deterministic Scoring Engine

The application uses a deterministic scoring engine instead of relying entirely on AI-generated scores.

Evaluation dimensions include:

- Market Opportunity
- Innovation
- Competition
- Scalability
- Technical Feasibility
- Revenue Model
- Execution Risk
- Market Timing
- Investor Readiness
- Product-Market Fit
- Startup Health Index

These dimensions are combined to generate a Startup Viability Score with explainable recommendations.

---

# Installation

Clone the repository.

```bash
git clone https://github.com/CHANDRASAI9491/AI-Startup-Idea-Validator.git
```

Navigate to the project.

```bash
cd AI-Startup-Idea-Validator
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the environment.

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

Example:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
TAVILY_API_KEY=YOUR_TAVILY_API_KEY
MODEL_NAME=gemini-2.5-flash
ENABLE_WEB_SEARCH=true
EXPORT_DIR=reports
```

---

# Running the Application

Start the Streamlit application.

```bash
streamlit run ui/streamlit_app.py
```

---

# Running Tests

```bash
pytest tests -v
```

---

# Generated Report

The generated report includes:

- Executive Summary
- Problem Statement
- Solution Overview
- Market Analysis
- Competitor Analysis
- SWOT Analysis
- Risk Assessment
- MVP Roadmap
- Go-To-Market Strategy
- Investor Readiness
- Startup Health Score
- Startup Viability Score
- Final Recommendation

---

# Future Enhancements

- User Authentication
- Startup Project History
- Multi-language Support
- Team Collaboration
- Cloud Deployment
- Advanced Business Analytics
- Investment Recommendation Engine
- Startup Portfolio Management

---

# Contributors

Developed by:

**Pothuri Chandra Sai**

---

# License

This project is released under the MIT License.
