# System Architecture & Multi-Agent DAG Specification

The **Development of AI Based Startup Idea Validator with Market Analysis Assistance** platform is built on a modular multi-agent graph architecture designed to validate, score, and advise early-stage startup founders.

```mermaid
graph TD
    User([Startup Founder]) -->|Input Concept| UI[Streamlit Enterprise SaaS UI]
    UI --> Orchestrator[Application Orchestrator]
    Orchestrator --> Planner[DeepAgents Strategic Planner]
    Planner --> Graph[LangGraph StateGraph Workflow]
    
    Graph --> Agent1[Web Search Agent]
    Agent1 -->|Tavily Research Snippets| State[(StartupState & Memory Store)]
    
    State --> Agent2[Market Analysis Agent]
    State --> Agent3[Competitor Analysis Agent]
    State --> Agent4[SWOT & Risk Agent]
    State --> Agent5[MVP Recommendation Agent]
    State --> Agent6[Go-To-Market Agent]
    
    Agent2 --> State
    Agent3 --> State
    Agent4 --> State
    Agent5 --> State
    Agent6 --> State
    
    State --> ScoringEngine[Deterministic 8-Dimension Scoring Engine]
    ScoringEngine --> Agent7[Validation Report Agent]
    Agent7 -->|Overall Score & Verdict| FinalReport[Validation Report]
    FinalReport --> Exporters[PDF / Markdown / JSON Exporters]
    FinalReport --> Advisor[Grounded AI Venture Advisor]
```

## Key Components

1. **State & Memory Layer (`state/`)**: Pydantic v2 schemas (`StartupState`) and JSON session persistence store (`MemoryStore`).
2. **Specialized Agent Teams (`agents/`)**: Specialized domain agents loaded via `PromptLoader` and powered by Google Gemini with Tavily web research.
3. **Services & Tools (`services/` & `tools/`)**: Real-time Tavily Search Service with deduplication and citation tracking, LLM Service, Dynamic Prompt Loader, and Report Exporters.
4. **Pipeline Orchestrator (`pipeline/`)**: LangGraph StateGraph workflow integrated with DeepAgents Strategic Planner.
5. **App & Interface (`app/` & `ui/`)**: Streamlit web dashboard with custom HTML/CSS design system and Plotly visualization charts.
