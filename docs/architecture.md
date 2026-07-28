# System Architecture & Multi-Agent DAG Specification

The AI Startup Idea Validator platform is built on a modular multi-agent graph architecture designed to validate, score, and advise early-stage startup founders.

```mermaid
graph TD
    User([Startup Founder]) -->|Input Concept| UI[Streamlit UI / CLI / FastAPI]
    UI --> Orchestrator[Application Orchestrator]
    Orchestrator --> Graph[Validation Graph DAG]
    
    Graph --> Agent1[Web Search Agent]
    Agent1 -->|DDG Search Snippets| State[(Agent State & Memory)]
    
    State --> Agent2[Market Analysis Agent]
    State --> Agent3[Competitor Agent]
    State --> Agent4[SWOT & Risk Agent]
    State --> Agent5[MVP Recommendation Agent]
    State --> Agent6[GTM Strategy Agent]
    
    Agent2 --> State
    Agent3 --> State
    Agent4 --> State
    Agent5 --> State
    Agent6 --> State
    
    State --> Agent7[Validation Report Agent]
    Agent7 -->|Overall Score & Verdict| FinalReport[Validation Report]
    FinalReport --> Advisor[Conversational Advisor Chat]
```

## Key Components

1. **State & Memory Layer (`state/`)**: Pydantic v2 schemas and JSON-backed persistence store.
2. **Specialized Agent Teams (`agents/`)**: Individual domain experts powered by Google Gemini LLMs with fallback heuristics.
3. **Tools & Scrapers (`tools/`)**: Real-time web search tool (DuckDuckGo), LLM JSON parsers, and report exporters.
4. **Pipeline Orchestrator (`pipeline/`)**: DAG controller (`ValidationGraph`) supporting step-by-step progress tracking.
5. **App & Delivery (`app/` & `ui/`)**: FastAPI REST API backend, CLI runner, and Streamlit web dashboard.
