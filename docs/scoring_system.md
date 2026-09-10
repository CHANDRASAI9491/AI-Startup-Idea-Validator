# Deterministic Scoring System Specification

The **AI Startup Idea Validator** utilizes a deterministic, mathematically grounded scoring engine implemented in `services/scoring_engine.py`. Unlike arbitrary LLM score generation, the deterministic engine calculates reproducible, explainable viability scores based on objective market metrics, competitive dynamics, and risk parameters.

---

## 1. Core 8-Dimension Viability Rubric

The overall viability score is calculated on a 100-point scale across 8 weighted dimensions:

| Dimension | Field Name | Max Points | Weight | Primary Calculation Drivers |
| :--- | :--- | :---: | :---: | :--- |
| **Market Opportunity** | `market_opportunity_score` | 20 | 20% | TAM ($B), SAM ($B), SOM ($B), and sector CAGR % |
| **Innovation & Differentiation** | `innovation_score` | 15 | 15% | Value proposition novelty, AI automation depth, and keyword differentiation |
| **Competition & Moat** | `competition_score` | 15 | 15% | Incumbent density, moat strength (network effects, switching costs, IP) |
| **Scalability Potential** | `scalability_score` | 15 | 15% | Software gross margins, geographic expandability, recurring revenue profile |
| **Technical Feasibility** | `technical_feasibility_score` | 10 | 10% | Feasibility of 4-week MVP, stack maturity, engineering complexity |
| **Revenue Model Viability** | `revenue_model_score` | 10 | 10% | Monetization mechanics (B2B SaaS, usage-based, marketplace) and willingness to pay |
| **Execution & Risk Resilience** | `execution_risk_score` | 10 | 10% | Inverse financial, technical, and regulatory risk severities |
| **Market Timing** | `market_timing_score` | 5 | 5% | Industry tailwinds, macro trends, and regulatory or technological catalysts |
| **Total Viability Index** | `total_viability_score` | **100** | **100%** | **Sum of all 8 dimension scores** |

---

## 2. Strategic Verdict Classification

The overall score is mapped to a clear strategic recommendation:

- **PROCEED** (&ge; 75 / 100): High market opportunity with manageable risks, clear differentiation, and strong MVP viability. Recommended for rapid prototype execution and founder validation.
- **PIVOT** (60 &ndash; 74 / 100): Promising core concept with notable headwinds (e.g., crowded competition, high CAC, or unclear moat). Refine target ICP or adjust feature differentiation before heavy engineering.
- **CAUTION** (45 &ndash; 59 / 100): Substantial execution, technical, or regulatory hurdles identified. Requires targeted de-risking and direct customer discovery prior to capital commitment.
- **STOP** (&lt; 45 / 100): High structural friction, minimal addressable demand, or entrenched incumbent dominance. Re-evaluate core problem statement.

---

## 3. Supplementary Decision & Investor Metrics

In addition to the 8 core dimensions, the scoring engine calculates secondary investor readiness metrics:

- **Investor Readiness Score** (0–100): Evaluates maturity and diligence readiness for institutional seed/angel fundraising.
- **Funding Probability** (0–100%): Projected likelihood of attracting early-stage venture backing based on market size and team roadmap.
- **Product-Market Fit (PMF) Index** (0–100): Gauges urgency of customer pain points relative to solution value proposition.
- **Startup Health Index** (0–100): Composite index balancing market readiness, risk severity, and timeline feasibility.
- **Overall Confidence Score** (0–100%): Reflects data density, source verification count, and cross-metric alignment.
