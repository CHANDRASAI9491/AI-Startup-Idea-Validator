import pytest
from unittest.mock import MagicMock, patch
from state.schema import (
    StartupIdea,
    StartupState,
    ValidationReport,
    MarketAnalysis,
    CompetitorAnalysis,
    CompetitorItem,
    SWOTAnalysis,
    MVPRecommendation,
    GTMStrategy,
    TargetPersona,
    RiskItem,
    MVPFeature
)
from services.scoring_engine import ScoringBreakdown
from agents.conversational_advisor import ConversationalAdvisor
from app.orchestrator import ApplicationOrchestrator


@pytest.fixture
def sample_startup_state():
    idea = StartupIdea(
        idea_text="AI Legal Contract Review Platform",
        target_industry="LegalTech",
        target_audience="Corporate Counsel",
        business_model="B2B SaaS",
        budget="$50k",
        timeline="3 Months"
    )
    report = ValidationReport(
        overall_viability_score=85,
        verdict="PROCEED",
        executive_summary="High market demand for legal automation.",
        market_score=88,
        competitor_score=80,
        risk_score=75,
        mvp_score=90,
        gtm_score=82,
        investor_readiness_score=84,
        funding_probability=78,
        pmf_score=86.0,
        confidence_score=90.0,
        key_takeaways=["Large TAM in legal AI", "Strong differentiation via deep extraction"],
        recommended_next_steps=["Build MVP with core contract parsing", "Conduct pilot with 5 law firms"],
        scoring_breakdown=ScoringBreakdown(
            market_opportunity_score=18,
            innovation_score=13,
            competition_score=12,
            scalability_score=13,
            technical_feasibility_score=8,
            revenue_model_score=9,
            execution_risk_score=7,
            market_timing_score=5,
            total_viability_score=85,
            verdict="PROCEED",
            reasoning_why=["Market opportunity is high", "Risk profile manageable with mitigations"]
        )
    )
    market = MarketAnalysis(
        tam_billions=25.0,
        sam_billions=5.0,
        som_billions=0.5,
        cagr_percentage=18.5,
        market_size_summary="Rapidly growing market driven by AI adoption.",
        key_growth_drivers=["Cost reduction", "Compliance automation"],
        target_personas=[
            TargetPersona(role="General Counsel", pain_points=["Slow contract turnarounds"], willingness_to_pay="High")
        ],
        market_readiness_score=85
    )
    competitor = CompetitorAnalysis(
        moat_assessment="Proprietary fine-tuned legal NLP models.",
        market_positioning_summary="Premium automated contract intelligence.",
        direct_competitors=[CompetitorItem(name="LegalFly"), CompetitorItem(name="Ironclad")],
        indirect_competitors=[CompetitorItem(name="Manual Paralegal Review")]
    )
    swot = SWOTAnalysis(
        overall_risk_score=4,
        financial_risk=3,
        technical_risk=5,
        regulatory_risk=4,
        strengths=["Specialized models", "Fast analysis"],
        weaknesses=["High initial GPU costs"],
        opportunities=["Expand into compliance"],
        threats=["Big Law building in-house tools"],
        risk_mitigation_plan=["Use quantized model deployment to manage inference costs"],
        risk_matrix=[
            RiskItem(risk_name="GPU Cost Overflow", category="Financial", severity_score=6, mitigation_strategy="Use serverless inference")
        ]
    )
    mvp = MVPRecommendation(
        core_value_proposition="Automate 80% of contract review in minutes.",
        tech_stack_frontend="React",
        tech_stack_backend="Python FastAPI",
        tech_stack_database="PostgreSQL",
        tech_stack_ai="Google Gemini 1.5 Flash",
        features=[
            MVPFeature(feature_name="PDF Contract Parser", priority="Must Have", estimated_days=7, description="Extract key clauses")
        ],
        four_week_roadmap={"Week 1": "Setup pipeline", "Week 2": "Contract parsing engine"},
        key_metrics_kpis=["Contract review speed", "Accuracy rate"]
    )
    gtm = GTMStrategy(
        primary_acquisition_channels=["LinkedIn Cold Outreach", "Legal Tech Conferences"],
        pricing_strategy="$499/month per seat",
        positioning_statement="The fastest AI legal assistant for in-house teams.",
        launch_tactics=["Free 14-day trial", "Direct demo calls"],
        estimated_cac_summary="$1,200 per enterprise account"
    )

    return StartupState(
        idea=idea,
        final_report=report,
        market_analysis=market,
        competitor_analysis=competitor,
        swot_analysis=swot,
        mvp_recommendation=mvp,
        gtm_strategy=gtm
    )


# 1. No report handling
def test_no_validation_report():
    advisor = ConversationalAdvisor()
    empty_state = StartupState(idea=StartupIdea(idea_text="Raw Idea"), final_report=None)
    response = advisor.answer_question("What is our market size?", empty_state)
    assert "No active validation report is available. Please validate a startup idea first." in response
    # Also test with state=None
    assert "No active validation report is available. Please validate a startup idea first." in advisor.answer_question("What is our market size?", None)


# 2. Market question uses report context
def test_market_question_uses_report(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    context = advisor.build_intent_context("market", sample_startup_state)
    assert "$25.0B" in context or "25.0" in context
    assert "Market Score" in context
    assert "General Counsel" in context


# 3. Competition question uses report context
def test_competition_question_uses_report(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    context = advisor.build_intent_context("competition", sample_startup_state)
    assert "LegalFly" in context
    assert "Ironclad" in context
    assert "Proprietary fine-tuned legal NLP models" in context


# 4. Risk question uses report context
def test_risk_question_uses_report(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    context = advisor.build_intent_context("risk", sample_startup_state)
    assert "GPU Cost Overflow" in context or "GPU costs" in context
    assert "Risk Score" in context


# 5. MVP question uses report context
def test_mvp_question_uses_report(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    context = advisor.build_intent_context("mvp", sample_startup_state)
    assert "React" in context
    assert "FastAPI" in context
    assert "PDF Contract Parser" in context


# 6. GTM question uses report context
def test_gtm_question_uses_report(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    context = advisor.build_intent_context("gtm", sample_startup_state)
    assert "LinkedIn Cold Outreach" in context
    assert "499" in context


# 7. Score / funding question uses report context
def test_score_funding_question_uses_report(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    score_ctx = advisor.build_intent_context("score", sample_startup_state)
    assert "85/100" in score_ctx or "85" in score_ctx

    funding_ctx = advisor.build_intent_context("funding", sample_startup_state)
    assert "78%" in funding_ctx or "78" in funding_ctx


# 8. Follow-up question inherits previous intent
def test_followup_question_inherits_intent():
    advisor = ConversationalAdvisor()
    history = [
        {"role": "user", "content": "What are the main risks?"},
        {"role": "assistant", "content": "The main risk is GPU costs."}
    ]

    intent = advisor.classify_intent("How can I reduce it?", chat_history=history)
    assert intent == "risk"

    assert advisor.should_search_web("How can I reduce it?", intent, "report_context") is False


# 9. Gemini report-grounded response returned
def test_gemini_report_grounded_response(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    with patch.object(advisor, "generate_text", return_value="### Direct Answer\nThe TAM is $25B."):
        answer = advisor.answer_question("What is the TAM?", sample_startup_state)
        assert "Direct Answer" in answer
        assert "$25B" in answer
        mock_tavily.search.assert_not_called()


# 10. Gemini unavailable report fallback
def test_gemini_unavailable_report_fallback(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    with patch.object(advisor, "generate_text", return_value=None):
        answer = advisor.answer_question("What is the biggest risk?", sample_startup_state)
        assert "Direct Answer" in answer
        assert "Evidence From Validation" in answer
        mock_tavily.search.assert_not_called()


# 11. Unsupported question safely handled
def test_unsupported_question_safely_handled(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    fallback = advisor.generate_grounded_fallback("What is the population of Tokyo?", "general", sample_startup_state)
    assert "does not contain enough evidence" in fallback


# 12. Tavily is NOT called when report has sufficient evidence
def test_tavily_not_called_when_report_sufficient(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    assert advisor.should_search_web("What is my viability score?", "score", "Score Context") is False
    assert advisor.should_search_web("What is my biggest risk?", "risk", "Risk Context") is False
    assert advisor.should_search_web("What features are in my MVP?", "mvp", "MVP Context") is False

    advisor.answer_question("What is my viability score?", sample_startup_state)
    mock_tavily.search.assert_not_called()


# 13. Tavily IS called when web research is required
def test_tavily_called_when_web_research_required(sample_startup_state):
    mock_tavily = MagicMock()
    mock_tavily.search.return_value = [
        {"title": "LegalFly Current Pricing 2026", "url": "https://legalfly.com/pricing", "snippet": "LegalFly starts at $300/mo."}
    ]
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    question = "What is the current competitor pricing for LegalFly?"
    assert advisor.should_search_web(question, "competition", "Report Context") is True

    answer = advisor.answer_question(question, sample_startup_state)
    mock_tavily.search.assert_called_once()
    assert "LegalFly" in answer


# 14. Tavily results are included in Gemini prompt
def test_tavily_results_included_in_gemini_prompt(sample_startup_state):
    mock_tavily = MagicMock()
    mock_tavily.search.return_value = [
        {"title": "Latest LegalTech AI Trends", "url": "https://legaltech.com/trends", "snippet": "Generative AI contract analysis growing rapidly."}
    ]
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    with patch.object(advisor, "generate_text", return_value="### Direct Answer\nLatest trends show rapid AI adoption.\n\n### Additional Web Research\n- [Latest LegalTech AI Trends] — https://legaltech.com/trends") as mock_gen:
        answer = advisor.answer_question("What are the latest market trends in 2026?", sample_startup_state)
        mock_gen.assert_called_once()
        prompt_arg = mock_gen.call_args[0][0]
        assert "Latest LegalTech AI Trends" in prompt_arg
        assert "https://legaltech.com/trends" in prompt_arg
        assert "Additional Web Research" in answer


# 15. Tavily failure falls back safely
def test_tavily_failure_falls_back_safely(sample_startup_state):
    mock_tavily = MagicMock()
    mock_tavily.search.side_effect = Exception("API connection timeout")
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    # Tavily search fails gracefully without raising exception
    results = advisor.search_web_for_advisor("What is the current pricing?", sample_startup_state, "gtm")
    assert results == []

    # Question answering still returns safe answer
    answer = advisor.answer_question("What is the current pricing?", sample_startup_state)
    assert answer is not None
    assert len(answer) > 0


# 16. Web sources are included in final answer when web research is used
def test_web_sources_included_in_final_answer_when_web_research_used(sample_startup_state):
    mock_tavily = MagicMock()
    mock_tavily.search.return_value = [
        {"title": "Recent Funding in LegalTech 2026", "url": "https://news.com/funding", "snippet": "LegalTech startups raised $500M."}
    ]
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    with patch.object(advisor, "generate_text", return_value=None):
        answer = advisor.answer_question("What is the recent funding in this space?", sample_startup_state)
        assert "### Additional Web Research" in answer
        assert "Recent Funding in LegalTech 2026" in answer
        assert "https://news.com/funding" in answer


# 17. Session ID handling in Orchestrator and Advisor
def test_session_id_handling_in_orchestrator(sample_startup_state):
    orchestrator = ApplicationOrchestrator()
    valid_session_id = "test_valid_session_123"
    orchestrator.memory.save_state(valid_session_id, sample_startup_state)

    # 1. Non-existent session returns clear message
    res_invalid = orchestrator.ask_advisor("non_existent_session_999", "What is our biggest risk?")
    assert "No active validation report is available. Please validate a startup idea first." in res_invalid

    # 2. Valid active session returns grounded answer
    with patch.object(orchestrator.advisor, "generate_text", return_value="### Direct Answer\nYour top risk is GPU Cost."):
        res_valid = orchestrator.ask_advisor(valid_session_id, "What is our biggest risk?")
        assert "GPU Cost" in res_valid


# 18. Suggested question flow & intent classification
def test_suggested_questions_and_followup_flow(sample_startup_state):
    advisor = ConversationalAdvisor()

    welcome_questions = [
        ("What is the biggest risk?", "risk"),
        ("What is our strongest competitive advantage?", "competition"),
        ("Is the market attractive enough?", "market"),
        ("What should we build in the MVP?", "mvp"),
        ("How should we acquire our first customers?", "gtm"),
        ("How can we improve our viability score?", "score"),
        ("What would investors question?", "funding"),
        ("What should we do next?", "general"),
    ]

    for q_text, expected_intent in welcome_questions:
        detected = advisor.classify_intent(q_text)
        assert detected == expected_intent, f"Expected intent '{expected_intent}' for question '{q_text}', got '{detected}'"


# 19. REGRESSION TEST BUG 1: Viability score question does not crash and handles scoring reasoning safely
def test_viability_score_question_regression_no_crash(sample_startup_state):
    mock_tavily = MagicMock()
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    # Test with valid scoring breakdown
    answer = advisor.answer_question("What is my viability score?", sample_startup_state)
    assert "85/100" in answer
    assert "PROCEED" in answer
    assert "Direct Answer" in answer
    assert "Why It Matters" in answer
    assert "Recommended Action" in answer
    assert "Evidence From Validation" in answer

    # Test with scoring breakdown that has no optional attributes (ensure no AttributeError)
    state_minimal = StartupState(
        idea=sample_startup_state.idea,
        final_report=ValidationReport(
            overall_viability_score=70,
            verdict="CAUTION",
            executive_summary="Requires refinement.",
            market_score=70,
            competitor_score=65,
            risk_score=60,
            mvp_score=75,
            gtm_score=68
        )
    )
    answer_minimal = advisor.answer_question("What is my viability score?", state_minimal)
    assert "70/100" in answer_minimal
    assert "CAUTION" in answer_minimal


# 20. REGRESSION TEST BUG 2: Current competitor question uses Tavily evidence in answer and does not just repeat positioning
def test_current_competitor_question_uses_tavily_evidence(sample_startup_state):
    mock_tavily = MagicMock()
    mock_tavily.search.return_value = [
        {
            "title": "ContractGenie AI (2026)",
            "url": "https://contractgenie.ai",
            "snippet": "ContractGenie AI launches enterprise automated contract parsing with real-time compliance checking."
        },
        {
            "title": "LexisNexis AI Contract Review",
            "url": "https://lexisnexis.com/ai-contracts",
            "snippet": "LexisNexis expands automated legal intelligence solutions in 2026."
        }
    ]
    advisor = ConversationalAdvisor(tavily_tool=mock_tavily)

    # In fallback mode (and in prompt generation)
    with patch.object(advisor, "generate_text", return_value=None):
        answer = advisor.answer_question("What are the latest competitors in this market in 2026?", sample_startup_state)
        mock_tavily.search.assert_called_once()
        assert "### Direct Answer" in answer
        assert "ContractGenie AI (2026)" in answer
        assert "LexisNexis" in answer
        assert "### Additional Web Research" in answer
        assert "https://contractgenie.ai" in answer
        assert "https://lexisnexis.com/ai-contracts" in answer


# 21. REGRESSION TEST BUG 3: Risk follow-up produces actionable mitigation instead of merely repeating the risk
def test_risk_followup_produces_mitigation_action_not_repeat_fact(sample_startup_state):
    advisor = ConversationalAdvisor()

    # Step 1: Fact question "What is the biggest risk?"
    with patch.object(advisor, "generate_text", return_value=None):
        ans_fact = advisor.answer_question("What is the biggest risk?", sample_startup_state)
        assert "The primary identified risk" in ans_fact
        assert "High initial GPU costs" in ans_fact

    # Step 2: Action question "How can I reduce this risk?"
    chat_hist = [
        {"role": "user", "content": "What is the biggest risk?"},
        {"role": "assistant", "content": ans_fact}
    ]
    with patch.object(advisor, "generate_text", return_value=None):
        ans_action = advisor.answer_question("How can I reduce this risk?", sample_startup_state, chat_history=chat_hist)
        assert "To reduce and mitigate the primary risk" in ans_action
        # Concrete mitigation from validation report
        assert "quantized model deployment" in ans_action or "serverless inference" in ans_action
        # Ensure it does not simply repeat the same phrasing as the fact question
        assert ans_action != ans_fact


# 22. Competitor names from report vs missing competitor names fallback
def test_competitor_names_from_report_and_missing_names_fallback(sample_startup_state):
    advisor = ConversationalAdvisor()

    # Case A: Competitors present in report
    with patch.object(advisor, "generate_text", return_value=None):
        ans_with_comps = advisor.answer_question("Who are my main competitors?", sample_startup_state)
        assert "Direct Competitors:" in ans_with_comps
        assert "LegalFly" in ans_with_comps
        assert "Ironclad" in ans_with_comps
        assert "Indirect Competitors:" in ans_with_comps
        assert "Manual Paralegal Review" in ans_with_comps

    # Case B: No competitor names in report
    state_no_comps = StartupState(
        idea=sample_startup_state.idea,
        final_report=sample_startup_state.final_report,
        competitor_analysis=CompetitorAnalysis(
            moat_assessment="Strong network effects and brand trust.",
            market_positioning_summary="Category leader in automated review.",
            direct_competitors=[],
            indirect_competitors=[]
        )
    )
    with patch.object(advisor, "generate_text", return_value=None):
        ans_no_comps = advisor.answer_question("Who are my main competitors?", state_no_comps)
        assert "Detailed competitor names are unavailable in the current report" in ans_no_comps
        assert "Strong network effects" in ans_no_comps or "Category leader" in ans_no_comps


# 23. Multi-turn follow-up intent inheritance is not fooled by assistant response text
def test_multi_turn_followup_intent_inheritance_not_fooled_by_assistant_text():
    advisor = ConversationalAdvisor()

    # Assistant response mentions Market Score, Risk Score, MVP Score, etc.
    assistant_resp = (
        "### Direct Answer\nYour TAM is $25B.\n\n"
        "### Evidence From Validation\nMarket Score: 88 | Risk Score: 75 | MVP Score: 90"
    )
    history = [
        {"role": "user", "content": "What is my market size?"},
        {"role": "assistant", "content": assistant_resp}
    ]

    # User asks "Why?" -> must inherit 'market', NOT 'risk'
    intent_why = advisor.classify_intent("Why?", chat_history=history)
    assert intent_why == "market"

    # User asks "Tell me more." -> must inherit 'market'
    intent_more = advisor.classify_intent("Tell me more.", chat_history=history)
    assert intent_more == "market"


# 24. Short follow-up questions intent resolution
def test_short_followup_questions_intent():
    advisor = ConversationalAdvisor()

    risk_history = [
        {"role": "user", "content": "What is the biggest risk?"},
        {"role": "assistant", "content": "HIPAA compliance is the biggest risk."}
    ]

    for short_q in ["Why?", "How?", "Can I reduce it?", "How can I improve it?", "What about that?", "Explain more."]:
        intent = advisor.classify_intent(short_q, chat_history=risk_history)
        assert intent == "risk", f"Failed for '{short_q}', got '{intent}'"
