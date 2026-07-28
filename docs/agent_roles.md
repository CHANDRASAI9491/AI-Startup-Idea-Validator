# Specialized Agent Roles & Data Contracts

## 1. Web Search Agent (`agents/web_search_agent.py`)
- **Role**: Real-time market researcher.
- **Input**: `StartupIdea`
- **Output**: `WebSearchResults` (5 query categories: Market Trends, Competitors, Customer Pain Points, Industry News, Funding).

## 2. Market Analysis Agent (`agents/market_analysis_agent.py`)
- **Role**: Venture Market Intelligence Analyst.
- **Input**: `StartupIdea`, `WebSearchResults`
- **Output**: `MarketAnalysis` (TAM, SAM, SOM, CAGR %, Growth Drivers, Target Personas).

## 3. Competitor Agent (`agents/competitor_agent.py`)
- **Role**: Competitive Intelligence Strategist.
- **Input**: `StartupIdea`, `WebSearchResults`
- **Output**: `CompetitorAnalysis` (Direct/Indirect Competitors, Feature Matrix, Moat Assessment).

## 4. SWOT & Risk Agent (`agents/swot_risk_agent.py`)
- **Role**: Venture Risk Auditor.
- **Input**: `StartupIdea`, `WebSearchResults`
- **Output**: `SWOTAnalysis` (SWOT Grid, Risk Ratings 1-10, Mitigation Plan).

## 5. MVP Recommendation Agent (`agents/mvp_recommendation_agent.py`)
- **Role**: Technical Product Manager.
- **Input**: `StartupIdea`
- **Output**: `MVPRecommendation` (Core Value Prop, Must/Should Have Features, Tech Stack, 4-Week Roadmap).

## 6. GTM Strategy Agent (`agents/gtm_strategy_agent.py`)
- **Role**: Growth Marketer.
- **Input**: `StartupIdea`
- **Output**: `GTMStrategy` (Acquisition Channels, Pricing Strategy, Launch Tactics, CAC Summary).

## 7. Report Synthesis Agent (`agents/report_agent.py`)
- **Role**: Managing VC Partner.
- **Input**: All Agent Outputs
- **Output**: `ValidationReport` (Viability Score 0-100, Verdict: PROCEED/PIVOT/CAUTION/STOP, Executive Summary, Recommended Next Steps).

## 8. Conversational Advisor (`agents/conversational_advisor.py`)
- **Role**: Interactive Startup Mentor.
- **Input**: User Question, `AgentState` Context, Chat History
- **Output**: Natural language advisory advice.
