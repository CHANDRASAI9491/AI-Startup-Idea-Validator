import pytest
from services.scoring_engine import DeterministicScoringEngine, ScoringBreakdown


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

    # Assert no false evidence limitations when real evidence is present
    assert len(sec_scores.evidence_limitations) == 0
    assert len(farm_scores.evidence_limitations) == 0
    assert len(food_scores.evidence_limitations) == 0


def test_scoring_with_missing_market_evidence():
    """Verify that None TAM and None CAGR do not award points and explain unweighted opportunity."""
    scores = DeterministicScoringEngine.calculate_scores(
        idea_text="AI Healthcare Diagnostic Assistant",
        target_industry="Healthcare",
        tam_billions=None,
        cagr_percentage=None,
        direct_competitor_count=2,
        moat_level="Strong"
    )
    assert scores is not None
    assert any("Market size could not be verified from available research; market opportunity unweighted." in r for r in scores.reasoning_why)
    assert "Market size could not be verified from available research." in scores.evidence_limitations
    # Ensure it did not add the massive market or high CAGR bonuses
    assert not any("Massive total addressable market" in r for r in scores.reasoning_why)
    assert not any("Substantial market size" in r for r in scores.reasoning_why)
    assert not any("High industry CAGR" in r for r in scores.reasoning_why)


def test_scoring_with_missing_competitor_evidence():
    """Verify that None competitor count does not receive the low-competition density bonus."""
    scores_unknown = DeterministicScoringEngine.calculate_scores(
        idea_text="AI Healthcare Diagnostic Assistant",
        target_industry="Healthcare",
        tam_billions=15.0,
        cagr_percentage=12.0,
        direct_competitor_count=None,
        moat_level="Medium"
    )
    assert any("Competitive landscape could not be verified from available research." in r for r in scores_unknown.reasoning_why)
    assert "Competitive landscape could not be verified from available research." in scores_unknown.evidence_limitations
    assert not any("Low direct competitor density" in r for r in scores_unknown.reasoning_why)

    # Compare with known 2 competitors (which should get +4 bonus)
    scores_known_two = DeterministicScoringEngine.calculate_scores(
        idea_text="AI Healthcare Diagnostic Assistant",
        target_industry="Healthcare",
        tam_billions=15.0,
        cagr_percentage=12.0,
        direct_competitor_count=2,
        moat_level="Medium"
    )
    assert scores_known_two.competition_score > scores_unknown.competition_score
    assert any("Low direct competitor density" in r for r in scores_known_two.reasoning_why)
    assert "Competitive landscape could not be verified from available research." not in scores_known_two.evidence_limitations


def test_scoring_with_verified_zero_competitors():
    """Verify that direct_competitor_count=0 (verified zero) is not treated as None."""
    scores_zero = DeterministicScoringEngine.calculate_scores(
        idea_text="Quantum Sensor for Deep Subterranean Exploration",
        target_industry="DeepTech",
        tam_billions=10.0,
        cagr_percentage=10.0,
        direct_competitor_count=0,
        moat_level="Strong"
    )
    # Verified 0 should receive low competitor density bonus and NOT add a limitation
    assert any("Low direct competitor density (0 incumbents)" in r for r in scores_zero.reasoning_why)
    assert not any("Competitive landscape could not be verified" in r for r in scores_zero.reasoning_why)
    assert "Competitive landscape could not be verified from available research." not in scores_zero.evidence_limitations


def test_phase3_test1_missing_market_evidence():
    """Phase 3 Test 1: Given tam_billions=None and cagr_percentage=None, verify calculation succeeds,
    no fabricated market values appear, evidence_limitations contains market limitation,
    and reasoning_why remains populated.
    """
    scores = DeterministicScoringEngine.calculate_scores(
        idea_text="Next-Gen Renewable Grid Management Platform",
        target_industry="CleanTech",
        tam_billions=None,
        cagr_percentage=None,
        direct_competitor_count=1
    )
    assert scores is not None
    assert isinstance(scores.total_viability_score, int)
    assert "Market size could not be verified from available research." in scores.evidence_limitations
    assert any("Market size could not be verified from available research" in r for r in scores.reasoning_why)


def test_phase3_test2_missing_competitor_evidence():
    """Phase 3 Test 2: Given direct_competitor_count=None, verify no low-competition bonus
    is awarded and evidence_limitations contains the competitive landscape limitation.
    """
    scores = DeterministicScoringEngine.calculate_scores(
        idea_text="Autonomous Underwater Mining Drone",
        target_industry="Robotics",
        tam_billions=25.0,
        cagr_percentage=14.0,
        direct_competitor_count=None
    )
    assert "Competitive landscape could not be verified from available research." in scores.evidence_limitations
    assert not any("Low direct competitor density" in r for r in scores.reasoning_why)


def test_phase3_test3_verified_zero_competitors():
    """Phase 3 Test 3: Given direct_competitor_count=0, verify no competitive evidence
    limitation is added and verified-zero scoring bonus (+4) remains intact.
    """
    scores = DeterministicScoringEngine.calculate_scores(
        idea_text="Novel Molecular Synthetic Engine",
        target_industry="BioTech",
        tam_billions=30.0,
        cagr_percentage=15.0,
        direct_competitor_count=0
    )
    assert "Competitive landscape could not be verified from available research." not in scores.evidence_limitations
    assert any("Low direct competitor density (0 incumbents)" in r for r in scores.reasoning_why)


def test_phase3_test4_real_evidence_no_false_limitations():
    """Phase 3 Test 4: Given valid TAM/CAGR and competitor count, verify no false
    evidence limitations are added and existing scoring behavior is preserved.
    """
    scores = DeterministicScoringEngine.calculate_scores(
        idea_text="Enterprise Identity Verification API",
        target_industry="Cybersecurity",
        tam_billions=20.0,
        cagr_percentage=16.0,
        direct_competitor_count=2
    )
    assert scores.evidence_limitations == []
    assert len(scores.reasoning_why) > 0


def test_phase3_test5_backward_compatibility():
    """Phase 3 Test 5: Verify reasoning_why remains available, ScoringBreakdown works with
    legacy dictionary payloads without evidence_limitations, and default is empty list.
    """
    # Legacy payload without evidence_limitations key
    legacy_data = {
        "market_opportunity_score": 14,
        "innovation_score": 11,
        "competition_score": 10,
        "scalability_score": 12,
        "technical_feasibility_score": 8,
        "revenue_model_score": 8,
        "execution_risk_score": 7,
        "market_timing_score": 4,
        "total_viability_score": 74,
        "verdict": "CAUTION",
        "reasoning_why": ["Deep technology elements provide IP", "Low direct competitor density"]
    }
    breakdown = ScoringBreakdown.model_validate(legacy_data)
    assert breakdown.reasoning_why == ["Deep technology elements provide IP", "Low direct competitor density"]
    assert breakdown.evidence_limitations == []
    assert breakdown.verdict == "CAUTION"


def test_historical_state_compatibility():
    """Verify that MarketAnalysis deserializes both legacy persisted payloads and new None fields."""
    from state.schema import MarketAnalysis

    # 1. Historical payload with explicit numbers
    legacy_payload = {
        "tam_billions": 15.0,
        "sam_billions": 3.5,
        "som_billions": 0.2,
        "cagr_percentage": 14.5,
        "market_size_summary": "Legacy report summary",
        "market_readiness_score": 78
    }
    legacy_model = MarketAnalysis.model_validate(legacy_payload)
    assert legacy_model.tam_billions == 15.0
    assert legacy_model.cagr_percentage == 14.5

    # 2. Modern payload with null/missing numbers
    modern_payload = {
        "tam_billions": None,
        "sam_billions": None,
        "som_billions": None,
        "cagr_percentage": None,
        "market_readiness_score": None
    }
    modern_model = MarketAnalysis.model_validate(modern_payload)
    assert modern_model.tam_billions is None
    assert modern_model.cagr_percentage is None
    assert "could not be established" in modern_model.market_size_summary
