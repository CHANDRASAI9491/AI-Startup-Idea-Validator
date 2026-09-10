# Agent Roles & Responsibilities

This document specifies the exact agent classes, modules, responsibilities, and data contracts implemented in the repository.

---

## 1. Strategic Planner (`tools/planning_tool.py` - `DeepAgentsPlanner`)
- **Module**: `tools/planning_tool.py`
- **Class**: `DeepAgentsPlanner`
- **Responsibility**: Analyzes the founder's initial idea and formulates a structured research plan, defining validation goals, key uncertainties, target search themes, and evaluation metrics.
- **Input**: `StartupIdea`
- **Output**: `DeepAgentsPlan`

---

## 2. Web Search Agent (`tools/tavily_tool.py` - `TavilySearchTool`)
- **Module**: `tools/tavily_tool.py` (and `agents/web_search_agent.py`)
- **Class**: `TavilySearchTool` / `WebSearchAgent`
- **Responsibility**: Connects to the Tavily Search API to perform real-time market search queries across five dimensions: Market Trends, Direct Competitors, Customer Pain Points, Industry News, and Funding Signals.
- **Input**: `idea_text: str`, `industry: str`
- **Output**: `WebSearchResults` (containing raw search results and categorized intelligence)

---

## 3. Market Analysis Agent (`agents/market_analysis_agent.py` - `MarketAnalysisAgent`)
- **Module**: `agents/market_analysis_agent.py`
- **Class**: `MarketAnalysisAgent` (and `market-research` Deep Agents subagent)
- **Responsibility**: Synthesizes web research to calculate Total Addressable Market (TAM), Serviceable Addressable Market (SAM), Serviceable Obtainable Market (SOM) in billions of USD, projected CAGR %, key growth drivers, and target buyer personas.
- **Input**: `StartupIdea`, `WebSearchResults`
- **Output**: `MarketAnalysis`

---

## 4. Competitor Analysis Agent (`agents/competitor_agent.py` - `CompetitorAgent`)
- **Module**: `agents/competitor_agent.py`
- **Class**: `CompetitorAgent` (and `competitor-research` Deep Agents subagent)
- **Responsibility**: Identifies incumbent competitors (direct and indirect), constructs feature comparison matrices, benchmarks pricing tiers, and assesses defensive moats (network effects, switching costs, proprietary technology).
- **Input**: `StartupIdea`, `WebSearchResults`
- **Output**: `CompetitorAnalysis`

---

## 5. SWOT & Risk Agent (`agents/swot_risk_agent.py` - `SWOTRiskAgent`)
- **Module**: `agents/swot_risk_agent.py`
- **Class**: `SWOTRiskAgent` (and `swot-risk` Deep Agents subagent)
- **Responsibility**: Compiles a 4-quadrant SWOT matrix (Strengths, Weaknesses, Opportunities, Threats) and constructs a risk register where each risk is assigned a category, probability (1–5), impact (1–5), severity score (1–25), and concrete mitigation strategy.
- **Input**: `StartupIdea`, `WebSearchResults`
- **Output**: `SWOTAnalysis`

---

## 6. MVP Scoping Agent (`agents/mvp_recommendation_agent.py` - `MVPRecommendationAgent`)
- **Module**: `agents/mvp_recommendation_agent.py`
- **Class**: `MVPRecommendationAgent` (and `mvp` Deep Agents subagent)
- **Responsibility**: Outlines the core value proposition, scopes Must-Have vs. Should-Have features with estimated engineering effort (days), recommends the production tech stack (frontend, backend, database, AI), and schedules a 4-week execution roadmap.
- **Input**: `StartupIdea`, `MarketAnalysis`, `CompetitorAnalysis`
- **Output**: `MVPRecommendation`

---

## 7. Go-To-Market Agent (`agents/gtm_strategy_agent.py` - `GTMStrategyAgent`)
- **Module**: `agents/gtm_strategy_agent.py`
- **Class**: `GTMStrategyAgent` (and `gtm` Deep Agents subagent)
- **Responsibility**: Formulates customer acquisition channels (e.g., PLG, outbound sales, content SEO), creates positioning statements, defines pricing strategies, and provides launch tactics and CAC estimates.
- **Input**: `StartupIdea`, `MarketAnalysis`, `CompetitorAnalysis`
- **Output**: `GTMStrategy`

---

## 8. Report Agent (`agents/report_agent.py` - `ReportAgent`)
- **Module**: `agents/report_agent.py`
- **Class**: `ReportAgent` (and `report` Deep Agents subagent)
- **Responsibility**: Synthesizes all domain intelligence into an executive summary, strategic verdict (`PROCEED`, `PIVOT`, `CAUTION`, `STOP`), key takeaways, and prioritized immediate next steps.
- **Input**: All preceding agent state attributes
- **Output**: `ValidationReport`

---

## 9. Deterministic Scoring Engine (`services/scoring_engine.py` - `DeterministicScoringEngine`)
- **Module**: `services/scoring_engine.py`
- **Class**: `DeterministicScoringEngine`
- **Responsibility**: Applies mathematical formulas across 8 objective dimensions to produce an explainable 0–100 overall viability score and supplementary investor readiness metrics.
- **Input**: Quantitative inputs from Market, Competitor, and SWOT state
- **Output**: `ScoringBreakdown`

---

## 10. AI Venture Advisor (`agents/conversational_advisor.py` - `ConversationalAdvisor`)
- **Module**: `agents/conversational_advisor.py`
- **Class**: `ConversationalAdvisor`
- **Responsibility**: Provides contextual follow-up guidance to founders, classifying user intents, referencing the active validation dossier, executing supplementary Tavily searches when live data is requested, and persisting multi-turn conversations in SQLite.
- **Input**: User question, `StartupState` context, conversation history
- **Output**: Context-grounded response text with citations
