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

- **PROCEED** (&ge; 78 / 100): High market opportunity with manageable risks, clear differentiation, and strong MVP viability. Recommended for rapid prototype execution and founder validation.
- **CAUTION** (65 &ndash; 77 / 100): Promising core concept with notable headwinds or unverified market/competitor evidence. Requires targeted de-risking and direct customer discovery prior to heavy engineering or capital commitment.
- **PIVOT** (50 &ndash; 64 / 100): Substantial execution, competitive, or structural friction identified. Refine target ICP, differentiation, or business model before proceeding.
- **STOP** (&lt; 50 / 100): High structural friction, minimal addressable demand, or entrenched incumbent dominance. Re-evaluate core problem statement.

The scoring engine is strictly deterministic: it does not use SHA-256 hash variance, seed offsets, or pseudo-random perturbations. Equivalent inputs with cosmetic punctuation or wording differences produce identical scores.

---

## 3. Supplementary Decision & Investor Metrics

In addition to the 8 core dimensions, the scoring engine calculates secondary investor readiness metrics:

- **Investor Readiness Score** (0–100): Evaluates maturity and diligence readiness for institutional seed/angel fundraising.
- **Funding Probability** (0–100%): Projected likelihood of attracting early-stage venture backing based on market size and team roadmap.
- **Product-Market Fit (PMF) Index** (0–100): Gauges urgency of customer pain points relative to solution value proposition.
- **Startup Health Index** (0–100): Composite index balancing market readiness, risk severity, and timeline feasibility.
- **Overall Confidence Score** (0–100%): Evidence-based metric strictly derived from validation completeness across live web research (25 pts), market sizing evidence (20 pts), competitive landscape verification (20 pts), SWOT/risk analysis (15 pts), MVP technical scope (10 pts), and GTM strategy (10 pts), bounded between 20% and 95% (capped at 65% when live web research is unavailable).
