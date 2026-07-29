# 🚀 AI Startup Idea Validator

An AI-powered, multi-agent startup validation platform that analyzes startup ideas and generates a comprehensive business validation report using Google Gemini, LangGraph, FastAPI, and Streamlit.

The system performs market research, competitor analysis, SWOT analysis, MVP planning, go-to-market strategy generation, and produces a final startup viability score with actionable recommendations.

---

## 📌 Overview

The **AI Startup Idea Validator** helps entrepreneurs and innovators evaluate startup ideas before investing time and resources.

Instead of manually researching the market, competitors, customer segments, and business risks, this application automates the entire validation process using multiple AI agents working together.

---

## ✨ Features

- 🤖 Multi-Agent AI Architecture
- 🔍 Live Web Search using DuckDuckGo
- 📊 Market Analysis
- ⚔️ Competitor Analysis
- 🛡 SWOT & Risk Assessment
- 🛠 MVP Feature Recommendation
- 🎯 Go-To-Market Strategy
- 📈 Startup Viability Score (0–100)
- 📄 AI-Generated Validation Report
- 💬 Conversational AI Advisor
- 🌐 Streamlit Web Interface
- ⚡ FastAPI REST API
- ✅ Automated Test Suite using Pytest

---

# 🧠 Multi-Agent Workflow

```text
User Startup Idea
        │
        ▼
Web Search Agent
        │
        ▼
Market Analysis Agent
        │
        ▼
Competitor Analysis Agent
        │
        ▼
SWOT & Risk Agent
        │
        ▼
MVP Recommendation Agent
        │
        ▼
Go-To-Market Agent
        │
        ▼
Validation Report Agent
        │
        ▼
Conversational AI Advisor
        │
        ▼
Final Startup Validation Report
```

---

# 🛠 Technology Stack

## Programming Language

- Python 3.11+

## AI Framework

- LangChain
- LangGraph
- Google Gemini 2.5 Flash

## Backend

- FastAPI
- Uvicorn

## Frontend

- Streamlit

## Search Engine

- DuckDuckGo Search

## Data Validation

- Pydantic

## Testing

- Pytest

---

# 📁 Project Structure

```text
AI-Startup-Idea-Validator/

├── app/
├── agents/
├── services/
├── tools/
├── pipeline/
├── state/
├── ui/
├── tests/
├── docs/
├── reports/
├── requirements.txt
├── README.md
└── .env.example
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/CHANDRASAI9491/AI-Startup-Idea-Validator.git
```

Move into the project

```bash
cd AI-Startup-Idea-Validator
```

Create Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate Environment

```bash
.venv\Scripts\activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

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

# ▶ Running the Project

## Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

---

## FastAPI Server

```bash
uvicorn app.main:app --reload
```

API Documentation

```
http://localhost:8000/docs
```

---

## Run Tests

```bash
pytest tests -v
```

---

# 📊 Generated Report Includes

- Executive Summary
- Market Analysis
- Industry Trends
- Competitor Analysis
- SWOT Analysis
- Risk Assessment
- MVP Recommendations
- Go-To-Market Strategy
- Startup Viability Score
- Final Recommendation

---

# 🎯 Project Goals

- Reduce startup validation time
- Automate market research
- Help founders make data-driven decisions
- Demonstrate practical multi-agent AI architecture
- Showcase LangGraph-based AI orchestration

---

# 🚀 Future Enhancements

- PDF Report Generation
- User Authentication
- Dashboard Analytics
- Docker Deployment
- Cloud Deployment
- Vector Database Integration
- Multi-LLM Support
- Startup History Dashboard

---

# 👥 Contributors

- **Pothuri Chandra Sai**
- Team Members

---

# 📄 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you find this project useful, consider giving it a **⭐ Star** on GitHub.
