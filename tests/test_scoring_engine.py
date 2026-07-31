import pytest
from services.scoring_engine import DeterministicScoringEngine


def test_deterministic_scoring_engine_different_scores():
    # 1. Cybersecurity SaaS (High Tech, High TAM, B2B SaaS)
    sec_scores = DeterministicScoringEngine.calculate_scores(
        idea_text="AI-powered autonomous cybersecurity threat detection SaaS for enterprise cloud infrastructure",
        target_industry="Cybersecurity SaaS",
        tam_billions=65.0,
        sam_billions=12.0,
        som_billions=0.5,
        cagr_percentage=18.5,
        direct_competitor_count=2,
        moat_level="Strong",
        financial_risk=3,
        technical_risk=4,
        regulatory_risk=3
    )

    # 2. Smart Farming (BioTech / IoT, Medium TAM)
    farm_scores = DeterministicScoringEngine.calculate_scores(
        idea_text="IoT sensor network and satellite computer vision for precision crop yield optimization",
        target_industry="AgriTech",
        tam_billions=15.0,
        sam_billions=3.0,
        som_billions=0.1,
        cagr_percentage=11.0,
        direct_competitor_count=3,
        moat_level="Medium",
        financial_risk=5,
        technical_risk=6,
        regulatory_risk=4
    )

    # 3. Food Delivery (Commoditized, Low Margin)
    food_scores = DeterministicScoringEngine.calculate_scores(
        idea_text="Local hyper-fast food delivery app for home cooked meals",
        target_industry="Consumer Services",
        tam_billions=8.0,
        sam_billions=1.5,
        som_billions=0.05,
        cagr_percentage=6.0,
        direct_competitor_count=8,
        moat_level="Low",
        financial_risk=8,
        technical_risk=3,
        regulatory_risk=5
    )

    # Assert that total viability scores are significantly different and evidence-based
    assert sec_scores.total_viability_score > farm_scores.total_viability_score
    assert farm_scores.total_viability_score > food_scores.total_viability_score

    assert sec_scores.total_viability_score >= 80
    assert food_scores.total_viability_score <= 70

    # Assert verdicts align
    assert sec_scores.verdict == "PROCEED"
    assert food_scores.verdict in ["CAUTION", "PIVOT", "STOP"]

    # Assert reasoning WHY is non-empty
    assert len(sec_scores.reasoning_why) >= 3
    assert len(food_scores.reasoning_why) >= 3
