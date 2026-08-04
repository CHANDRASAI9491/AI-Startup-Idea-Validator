import re
import hashlib
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from services.logger import get_logger

logger = get_logger(__name__)


class RiskFactor(BaseModel):
    name: str
    category: str  # Financial, Technical, Market, Regulatory, Execution
    probability: int = Field(..., ge=1, le=5, description="Probability 1-5")
    impact: int = Field(..., ge=1, le=5, description="Impact 1-5")
    severity: int = Field(default=5, description="Probability x Impact (1-25)")
    mitigation: str = ""


class ScoringBreakdown(BaseModel):
    market_opportunity_score: int = Field(..., ge=0, le=20, description="Max 20")
    innovation_score: int = Field(..., ge=0, le=15, description="Max 15")
    competition_score: int = Field(..., ge=0, le=15, description="Max 15")
    scalability_score: int = Field(..., ge=0, le=15, description="Max 15")
    technical_feasibility_score: int = Field(..., ge=0, le=10, description="Max 10")
    revenue_model_score: int = Field(..., ge=0, le=10, description="Max 10")
    execution_risk_score: int = Field(..., ge=0, le=10, description="Max 10")
    market_timing_score: int = Field(..., ge=0, le=5, description="Max 5")
    total_viability_score: int = Field(..., ge=0, le=100, description="Total out of 100")

    # Additional Investor & Decision Metrics
    investor_readiness_score: int = Field(default=75, description="0-100")
    funding_probability: int = Field(default=65, description="0-100%")
    pmf_score: int = Field(default=70, description="0-100 Product-Market Fit")
    innovation_index: int = Field(default=80, description="0-100")
    competitive_strength: int = Field(default=72, description="0-100")
    business_complexity: int = Field(default=5, description="1-10")
    technical_complexity: int = Field(default=5, description="1-10")
    growth_potential: int = Field(default=78, description="0-100")
    startup_health_index: int = Field(default=76, description="0-100")
    overall_confidence_score: int = Field(default=85, description="0-100%")

    verdict: str = Field(default="PROCEED", description="PROCEED, PIVOT, CAUTION, STOP")
    reasoning_why: List[str] = Field(default_factory=list, description="Explainable reasoning points")


class DeterministicScoringEngine:
    """Deterministic evidence-driven scoring engine evaluating startup viability and investor readiness."""

    @staticmethod
    def _deterministic_seed_offset(text: str) -> int:
        """Derives a deterministic integer offset (-3 to +3) from text content hashing."""
        hash_val = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)
        return (hash_val % 7) - 3

    @classmethod
    def calculate_scores(
        cls,
        idea_text: str,
        target_industry: str,
        tam_billions: float = 10.0,
        sam_billions: float = 2.5,
        som_billions: float = 0.1,
        cagr_percentage: float = 12.5,
        direct_competitor_count: int = 3,
        moat_level: str = "Medium",
        financial_risk: int = 5,
        technical_risk: int = 5,
        regulatory_risk: int = 4
    ) -> ScoringBreakdown:
        text_lower = idea_text.lower()
        industry_lower = target_industry.lower()
        reasoning = []

        seed_offset = cls._deterministic_seed_offset(idea_text)

        # 1. MARKET OPPORTUNITY (Max 20)
        mkt_score = 10
        if tam_billions >= 50.0:
            mkt_score += 6
            reasoning.append(f"Massive total addressable market (${tam_billions}B TAM) provides high revenue ceiling (+6 market score).")
        elif tam_billions >= 10.0:
            mkt_score += 4
            reasoning.append(f"Substantial market size (${tam_billions}B TAM) supports expansion (+4 market score).")
        elif tam_billions >= 2.0:
            mkt_score += 2
        else:
            reasoning.append(f"Niche addressable market (${tam_billions}B TAM) limits multi-billion growth potential.")

        if cagr_percentage >= 15.0:
            mkt_score += 4
            reasoning.append(f"High industry CAGR of {cagr_percentage}% indicates strong market tailwinds (+4 market score).")
        elif cagr_percentage >= 8.0:
            mkt_score += 2

        mkt_score = max(min(mkt_score + (seed_offset % 2), 20), 4)

        # 2. INNOVATION & DIFFERENTIATION (Max 15)
        inn_score = 7
        high_tech_keywords = ["ai", "machine learning", "deep learning", "nlp", "llm", "quantum", "biotech", "genomics", "autonomous", "robotics", "cybersecurity", "sdk", "agentic"]
        low_moat_keywords = ["food delivery", "laundry", "cleaning", "marketplace", "directory", "voting", "social network", "taxis", "rental"]

        if any(kw in text_lower or kw in industry_lower for kw in high_tech_keywords):
            inn_score += 6
            reasoning.append("Deep technology elements provide proprietary IP and product differentiation (+6 innovation score).")
        elif any(kw in text_lower for kw in low_moat_keywords):
            inn_score -= 3
            reasoning.append("Commoditized business model faces low technology barriers to entry (-3 innovation score).")

        if "patent" in text_lower or "proprietary" in text_lower or "algorithm" in text_lower or "fine-tuned" in text_lower:
            inn_score += 2

        inn_score = max(min(inn_score + seed_offset, 15), 2)

        # 3. COMPETITION & MOAT (Max 15)
        comp_score = 10
        if direct_competitor_count <= 2:
            comp_score += 4
            reasoning.append(f"Low direct competitor density ({direct_competitor_count} incumbents) offers first-mover space (+4 competition score).")
        elif direct_competitor_count >= 6:
            comp_score -= 4
            reasoning.append(f"Saturated market with {direct_competitor_count}+ direct competitors (-4 competition score).")

        if moat_level.lower() in ["strong", "high", "defensible"]:
            comp_score += 3

        comp_score = max(min(comp_score, 15), 2)

        # 4. SCALABILITY POTENTIAL (Max 15)
        scale_score = 9
        if any(kw in text_lower or kw in industry_lower for kw in ["saas", "software", "api", "cloud", "platform", "b2b", "automation"]):
            scale_score += 5
            reasoning.append("Software/SaaS architecture yields high gross margins and low marginal distribution cost (+5 scalability score).")
        elif any(kw in text_lower for kw in ["delivery", "hardware", "logistics", "clinic", "physical", "warehouse"]):
            scale_score -= 4
            reasoning.append("Physical operations and logistics create linear friction costs (-4 scalability score).")

        scale_score = max(min(scale_score, 15), 3)

        # 5. TECHNICAL FEASIBILITY (Max 10)
        tech_score = max(10 - (technical_risk // 2), 2)

        # 6. REVENUE MODEL VIABILITY (Max 10)
        rev_score = 8
        if any(kw in text_lower for kw in ["subscription", "recurring", "b2b", "enterprise", "usage-based", "seat-based"]):
            rev_score += 2
            reasoning.append("Predictable recurring revenue model yields strong enterprise LTV/CAC ratios (+2 revenue score).")
        elif "ads" in text_lower or "freemium" in text_lower:
            rev_score -= 1

        rev_score = max(min(rev_score, 10), 3)

        # 7. EXECUTION & RISK RESILIENCE (Max 10)
        avg_risk = (financial_risk + technical_risk + regulatory_risk) / 3.0
        exec_risk_score = max(int(10 - (avg_risk * 0.8)), 2)

        # 8. MARKET TIMING (Max 5)
        timing_score = 4
        if "regulatory" in text_lower or regulatory_risk >= 7:
            timing_score -= 1
        if "ai" in text_lower or "automation" in text_lower or "security" in text_lower:
            timing_score += 1

        timing_score = max(min(timing_score, 5), 1)

        # TOTAL SCORE COMPUTATION
        total_viability = mkt_score + inn_score + comp_score + scale_score + tech_score + rev_score + exec_risk_score + timing_score
        total_viability = max(min(total_viability, 98), 25)

        # VERDICT CLASSIFICATION
        if total_viability >= 78:
            verdict = "PROCEED"
        elif total_viability >= 65:
            verdict = "CAUTION"
        elif total_viability >= 50:
            verdict = "PIVOT"
        else:
            verdict = "STOP"

        # DERIVED INVESTOR METRICS
        investor_readiness = max(min(int(total_viability * 0.95 + 3), 98), 20)
        funding_prob = max(min(int(total_viability * 0.88 + 2), 95), 15)
        pmf_score = max(min(int((mkt_score + comp_score) * 2.8), 96), 25)
        innovation_index = int((inn_score / 15.0) * 100)
        comp_strength = int((comp_score / 15.0) * 100)
        bus_complexity = max(min(int((10 - rev_score) + 4), 10), 1)
        tech_complexity = max(min(technical_risk, 10), 1)
        growth_potential = int((mkt_score + scale_score) / 35.0 * 100)
        startup_health = int((total_viability + investor_readiness) / 2.0)
        confidence = 90 if len(idea_text) > 100 else 75

        return ScoringBreakdown(
            market_opportunity_score=mkt_score,
            innovation_score=inn_score,
            competition_score=comp_score,
            scalability_score=scale_score,
            technical_feasibility_score=tech_score,
            revenue_model_score=rev_score,
            execution_risk_score=exec_risk_score,
            market_timing_score=timing_score,
            total_viability_score=total_viability,
            investor_readiness_score=investor_readiness,
            funding_probability=funding_prob,
            pmf_score=pmf_score,
            innovation_index=innovation_index,
            competitive_strength=comp_strength,
            business_complexity=bus_complexity,
            technical_complexity=tech_complexity,
            growth_potential=growth_potential,
            startup_health_index=startup_health,
            overall_confidence_score=confidence,
            verdict=verdict,
            reasoning_why=reasoning
        )
