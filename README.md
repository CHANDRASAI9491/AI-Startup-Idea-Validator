# AI Startup Idea Validator

## Overview

AI Startup Idea Validator is a multi-agent AI platform that helps entrepreneurs evaluate startup ideas before investing time and resources. The application combines DeepAgents, LangGraph, Google Gemini, and live web search to generate an evidence-based startup validation report.

The platform analyzes a startup idea from multiple perspectives, including market opportunity, competition, business feasibility, technical complexity, risks, and go-to-market strategy. Each specialized AI agent contributes to the final evaluation, producing a comprehensive report with explainable recommendations instead of generic AI-generated responses.

---

# Features

- Multi-agent AI architecture using DeepAgents
- LangGraph workflow orchestration
- Google Gemini integration
- Live market research using DuckDuckGo Search
- Market opportunity analysis
- Competitor analysis
- SWOT analysis
- Risk assessment
- MVP recommendation
- Go-to-market strategy
- Deterministic scoring engine
- Startup viability score
- AI conversational advisor
- Professional Streamlit interface
- Interactive charts and visualizations
- Export validation reports

---

# Architecture

```
User
        │
        ▼
Streamlit Interface
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
        ▼
Web Search Agent
        │
Market Analysis Agent
        │
Competitor Analysis Agent
        │
SWOT & Risk Agent
        │
MVP Recommendation Agent
        │
Go-To-Market Agent
        │
Validation Report Agent
        │
Conversational Advisor
        │
        ▼
Google Gemini
DuckDuckGo Search
        │
        ▼
Startup Validation Report
```

---

# Project Structure

```
AI-Startup-Idea-Validator/

app/
agents/
pipeline/
services/
state/
tools/
ui/
tests/
docs/
reports/
requirements.txt
README.md
.env.example
```

---

# Technology Stack

## Programming Language

- Python 3.11+

## AI Frameworks

- DeepAgents
- LangGraph
- LangChain

## Large Language Model

- Google Gemini 2.5 Flash

## Frontend

- Streamlit

## Search

- DuckDuckGo Search (DDGS)

## Data Validation

- Pydantic

## Visualization

- Plotly

## Testing

- Pytest

---

# Core Components

## Web Search Agent

Collects live market information, industry trends, competitors, and customer pain points.

## Market Analysis Agent

Evaluates market size, growth rate, customer segments, and business opportunity.

## Competitor Analysis Agent

Analyzes direct and indirect competitors, competitive advantages, and market gaps.

## SWOT & Risk Agent

Generates SWOT analysis and evaluates technical, market, financial, and execution risks.

## MVP Recommendation Agent

Suggests essential product features, development roadmap, and implementation priorities.

## Go-To-Market Agent

Creates pricing strategy, marketing channels, customer acquisition strategy, and launch roadmap.

## Validation Report Agent

Combines all agent outputs into a structured startup validation report.

## Conversational Advisor

Allows users to ask follow-up questions based on the generated report.

---

# Scoring Engine

The project uses a deterministic scoring engine instead of relying entirely on LLM-generated scores.

Evaluation dimensions include:

- Market Opportunity
- Innovation
- Competition
- Scalability
- Technical Feasibility
- Revenue Model
- Execution Risk
- Market Timing

Each dimension contributes to the overall Startup Viability Score.

---

# Installation

Clone the repository

```bash
git clone https://github.com/CHANDRASAI9491/AI-Startup-Idea-Validator.git
```

Move into the project

```bash
cd AI-Startup-Idea-Validator
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
MODEL_NAME=gemini-2.5-flash
ENABLE_WEB_SEARCH=true
MAX_SEARCH_RESULTS=5
EXPORT_DIR=reports
```

---

# Running the Application

Start the Streamlit application

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

Each validation report includes:

- Executive Summary
- Problem Statement
- Solution Overview
- Market Analysis
- Competitor Analysis
- SWOT Analysis
- Risk Assessment
- MVP Roadmap
- Go-To-Market Strategy
- Startup Viability Score
- Final Recommendation

---

# Future Enhancements

- Investor Readiness Assessment
- Product-Market Fit Analysis
- Funding Probability Prediction
- Multi-language Support
- User Authentication
- Project History
- Cloud Deployment
- Docker Support
- Team Collaboration
- Advanced Analytics Dashboard

---

# Contributors

- Pothuri Chandra Sai
- Team Members

---

# License

This project is licensed under the MIT License.
