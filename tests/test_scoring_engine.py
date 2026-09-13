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


def test_phase4_test_a_punctuation_does_not_change_score():
    """Phase 4 Test A: Verify that punctuation alone does not alter any dimension or total score."""
    desc_a = "AI medical coding automation platform"
    desc_b = "AI medical coding automation platform."

    score_a = DeterministicScoringEngine.calculate_scores(
        idea_text=desc_a,
        target_industry="Healthcare",
        tam_billions=10.0,
        sam_billions=2.0,
        som_billions=0.1,
        cagr_percentage=12.0,
        direct_competitor_count=4,
        moat_level="Medium",
        financial_risk=5,
        technical_risk=5,
        regulatory_risk=4
    )
    score_b = DeterministicScoringEngine.calculate_scores(
        idea_text=desc_b,
        target_industry="Healthcare",
        tam_billions=10.0,
        sam_billions=2.0,
        som_billions=0.1,
        cagr_percentage=12.0,
        direct_competitor_count=4,
        moat_level="Medium",
        financial_risk=5,
        technical_risk=5,
        regulatory_risk=4
    )

    assert score_a.total_viability_score == score_b.total_viability_score
    assert score_a.innovation_score == score_b.innovation_score
    assert score_a.market_opportunity_score == score_b.market_opportunity_score
    assert score_a.verdict == score_b.verdict


def test_phase4_test_b_same_fundamentals_produce_same_score():
    """Phase 4 Test B: Verify that semantically equivalent descriptions with formatting differences produce identical scores."""
    desc_clean = "B2B SaaS platform for enterprise cloud security orchestration"
    desc_spaced = "  B2B SaaS platform for enterprise cloud security orchestration   \n"

    score_1 = DeterministicScoringEngine.calculate_scores(
        idea_text=desc_clean,
        target_industry="Cybersecurity",
        tam_billions=25.0,
        cagr_percentage=15.0,
        direct_competitor_count=2,
        moat_level="Strong"
    )
    score_2 = DeterministicScoringEngine.calculate_scores(
        idea_text=desc_spaced,
        target_industry="Cybersecurity",
        tam_billions=25.0,
        cagr_percentage=15.0,
        direct_competitor_count=2,
        moat_level="Strong"
    )

    assert score_1.total_viability_score == score_2.total_viability_score
    assert score_1.innovation_score == score_2.innovation_score
    assert score_1.market_opportunity_score == score_2.market_opportunity_score
    assert score_1.competition_score == score_2.competition_score
    assert score_1.scalability_score == score_2.scalability_score
    assert score_1.technical_feasibility_score == score_2.technical_feasibility_score
    assert score_1.revenue_model_score == score_2.revenue_model_score
    assert score_1.execution_risk_score == score_2.execution_risk_score
    assert score_1.market_timing_score == score_2.market_timing_score
    assert score_1.verdict == score_2.verdict


def test_confidence_independent_of_idea_length():
    """Mandatory Test 1: Confidence is identical for short vs long descriptions with identical evidence."""
    short_idea = "AI app"
    long_idea = (
        "AI-powered enterprise contract intelligence and automated regulatory compliance orchestration "
        "platform designed for multi-jurisdictional legal operations and institutional risk mitigation."
    )
    assert len(short_idea) < 20
    assert len(long_idea) > 100

    score_short = DeterministicScoringEngine.calculate_scores(
        idea_text=short_idea,
        target_industry="LegalTech",
        tam_billions=15.0,
        cagr_percentage=12.0,
        direct_competitor_count=3,
        moat_level="Medium",
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )
    score_long = DeterministicScoringEngine.calculate_scores(
        idea_text=long_idea,
        target_industry="LegalTech",
        tam_billions=15.0,
        cagr_percentage=12.0,
        direct_competitor_count=3,
        moat_level="Medium",
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )

    assert score_short.overall_confidence_score == score_long.overall_confidence_score


def test_confidence_increases_with_evidence():
    """Mandatory Test 2: Strong/complete evidence produces higher confidence than weak/limited evidence."""
    score_weak = DeterministicScoringEngine.calculate_scores(
        idea_text="AI idea",
        target_industry="Tech",
        tam_billions=None,
        cagr_percentage=None,
        direct_competitor_count=None,
        has_web_research=False,
        has_swot=False,
        has_mvp=False,
        has_gtm=False
    )
    score_strong = DeterministicScoringEngine.calculate_scores(
        idea_text="AI idea",
        target_industry="Tech",
        tam_billions=25.0,
        sam_billions=5.0,
        som_billions=0.5,
        cagr_percentage=15.0,
        direct_competitor_count=2,
        moat_level="Strong",
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )

    assert score_strong.overall_confidence_score > score_weak.overall_confidence_score
    assert score_strong.overall_confidence_score >= 90
    assert score_weak.overall_confidence_score <= 40


def test_missing_web_research_reduces_confidence():
    """Mandatory Test 3: Unavailable live web research reduces confidence compared to otherwise equivalent state."""
    score_researched = DeterministicScoringEngine.calculate_scores(
        idea_text="Autonomous Supply Chain AI",
        target_industry="Logistics",
        tam_billions=30.0,
        cagr_percentage=14.0,
        direct_competitor_count=3,
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )
    score_unresearched = DeterministicScoringEngine.calculate_scores(
        idea_text="Autonomous Supply Chain AI",
        target_industry="Logistics",
        tam_billions=30.0,
        cagr_percentage=14.0,
        direct_competitor_count=3,
        has_web_research=False,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )

    assert score_researched.overall_confidence_score > score_unresearched.overall_confidence_score
    assert score_unresearched.overall_confidence_score <= 65


def test_missing_market_evidence_reduces_confidence():
    """Mandatory Test 4: Missing TAM/CAGR evidence reduces confidence."""
    score_with_market = DeterministicScoringEngine.calculate_scores(
        idea_text="Cybersecurity Threat Detection",
        target_industry="Cybersecurity",
        tam_billions=50.0,
        cagr_percentage=18.0,
        direct_competitor_count=2,
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )
    score_without_market = DeterministicScoringEngine.calculate_scores(
        idea_text="Cybersecurity Threat Detection",
        target_industry="Cybersecurity",
        tam_billions=None,
        cagr_percentage=None,
        direct_competitor_count=2,
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )

    assert score_with_market.overall_confidence_score > score_without_market.overall_confidence_score


def test_missing_competitor_evidence_reduces_confidence():
    """Mandatory Test 5: Missing competitor evidence (count=None) reduces confidence."""
    score_with_comp = DeterministicScoringEngine.calculate_scores(
        idea_text="DevOps Code Review Tool",
        target_industry="Developer Tools",
        tam_billions=20.0,
        cagr_percentage=12.0,
        direct_competitor_count=4,
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )
    score_without_comp = DeterministicScoringEngine.calculate_scores(
        idea_text="DevOps Code Review Tool",
        target_industry="Developer Tools",
        tam_billions=20.0,
        cagr_percentage=12.0,
        direct_competitor_count=None,
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )

    assert score_with_comp.overall_confidence_score > score_without_comp.overall_confidence_score


def test_missing_analysis_evidence_reduces_confidence():
    """Mandatory Test 6: Missing SWOT, MVP, or GTM evidence individually reduces confidence."""
    base_kwargs = dict(
        idea_text="FinTech Payment Routing Engine",
        target_industry="FinTech",
        tam_billions=40.0,
        cagr_percentage=16.0,
        direct_competitor_count=3,
        has_web_research=True
    )

    full_score = DeterministicScoringEngine.calculate_scores(
        **base_kwargs, has_swot=True, has_mvp=True, has_gtm=True
    )
    no_swot_score = DeterministicScoringEngine.calculate_scores(
        **base_kwargs, has_swot=False, has_mvp=True, has_gtm=True
    )
    no_mvp_score = DeterministicScoringEngine.calculate_scores(
        **base_kwargs, has_swot=True, has_mvp=False, has_gtm=True
    )
    no_gtm_score = DeterministicScoringEngine.calculate_scores(
        **base_kwargs, has_swot=True, has_mvp=True, has_gtm=False
    )

    assert full_score.overall_confidence_score > no_swot_score.overall_confidence_score
    assert full_score.overall_confidence_score > no_mvp_score.overall_confidence_score
    assert full_score.overall_confidence_score > no_gtm_score.overall_confidence_score


def test_verified_zero_competitors_is_not_missing():
    """Mandatory Test 7: Verified zero competitors (count=0) receives evidence credit and is not treated as missing."""
    score_verified_zero = DeterministicScoringEngine.calculate_scores(
        idea_text="Sub-orbital Satellite Inspection Drones",
        target_industry="SpaceTech",
        tam_billions=10.0,
        cagr_percentage=15.0,
        direct_competitor_count=0,
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )
    score_missing_competitors = DeterministicScoringEngine.calculate_scores(
        idea_text="Sub-orbital Satellite Inspection Drones",
        target_industry="SpaceTech",
        tam_billions=10.0,
        cagr_percentage=15.0,
        direct_competitor_count=None,
        has_web_research=True,
        has_swot=True,
        has_mvp=True,
        has_gtm=True
    )

    assert score_verified_zero.overall_confidence_score > score_missing_competitors.overall_confidence_score
    assert score_verified_zero.overall_confidence_score >= 90


def test_confidence_is_deterministic():
    """Mandatory Test 8: Identical state evaluated repeatedly produces exactly the same confidence score."""
    scores = [
        DeterministicScoringEngine.calculate_scores(
            idea_text="Healthcare Clinical Trial Matching AI",
            target_industry="HealthTech",
            tam_billions=18.0,
            cagr_percentage=13.5,
            direct_competitor_count=2,
            moat_level="Strong",
            has_web_research=True,
            has_swot=True,
            has_mvp=True,
            has_gtm=True
        ).overall_confidence_score
        for _ in range(50)
    ]
    assert all(s == scores[0] for s in scores)


def test_confidence_bounded():
    """Mandatory Test 9: Confidence score is strictly bounded within 0–100 across varied states."""
    test_cases = [
        dict(idea_text="", target_industry="", tam_billions=None, cagr_percentage=None, direct_competitor_count=None, has_web_research=False, has_swot=False, has_mvp=False, has_gtm=False),
        dict(idea_text="App", target_industry="Tech", tam_billions=5.0, cagr_percentage=None, direct_competitor_count=None, has_web_research=True, has_swot=False, has_mvp=True, has_gtm=False),
        dict(idea_text="Enterprise Platform", target_industry="Enterprise SaaS", tam_billions=100.0, sam_billions=20.0, som_billions=2.0, cagr_percentage=25.0, direct_competitor_count=1, moat_level="Strong", has_web_research=True, has_swot=True, has_mvp=True, has_gtm=True)
    ]
    for case in test_cases:
        score = DeterministicScoringEngine.calculate_scores(**case)
        assert 0 <= score.overall_confidence_score <= 100


def test_confidence_regression_score_dimensions_unchanged():
    """Mandatory Test 10: Score dimensions, total viability score, and verdict remain unchanged for identical scoring inputs."""
    scores = DeterministicScoringEngine.calculate_scores(
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
    assert scores.market_opportunity_score == 20
    assert scores.innovation_score == 13
    assert scores.competition_score == 15
    assert scores.scalability_score == 14
    assert scores.technical_feasibility_score == 8
    assert scores.revenue_model_score == 10
    assert scores.execution_risk_score == 7
    assert scores.market_timing_score == 5
    assert scores.total_viability_score == 92
    assert scores.verdict == "PROCEED"
