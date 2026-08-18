import logging
from typing import List, Dict, Optional, Any
from agents.base_agent import BaseAgent
from state.schema import StartupState
from services.logger import get_logger
from tools.tavily_tool import TavilySearchTool

logger = get_logger(__name__)


class ConversationalAdvisor(BaseAgent):
    """Grounded Strategic AI Venture Advisor supporting report-first evidence and Tavily web research fallback."""

    INTENT_KEYWORDS: Dict[str, List[str]] = {
        "risk": [
            "risk", "swot", "threat", "weakness", "mitigat", "vulnerability",
            "hazard", "pitfall", "downside", "fail", "financial risk",
            "technical risk", "regulatory risk", "severity", "danger", "obstacle",
            "reduce this risk", "reduce risk", "mitigate risk", "how to reduce"
        ],
        "competition": [
            "competitor", "competition", "moat", "differentiate", "positioning",
            "alternative", "rival", "substitute", "landscape", "matrix",
            "advantage", "benchmark", "edge", "barrier"
        ],
        "mvp": [
            "mvp", "prototype", "feature", "tech stack", "roadmap", "build",
            "frontend", "backend", "database", "kpi", "launch date", "timeline",
            "architecture", "product", "minimum viable", "v1", "scope"
        ],
        "gtm": [
            "gtm", "go-to-market", "go to market", "channel", "acquisition", "acquire",
            "cac", "pricing", "monetiz", "sales", "launch tactic", "marketing",
            "funnel", "customer acquisition", "distribution", "first customer", "outreach"
        ],
        "funding": [
            "fund", "investor", "readiness", "pmf", "pitch", "raise", "capital",
            "venture", "vc", "probability", "seed", "angel", "product-market fit",
            "product market fit", "fundraising", "valuation", "term sheet"
        ],
        "score": [
            "score", "viability", "breakdown", "verdict", "rating", "evaluate",
            "metric", "grade", "reasoning", "points", "sub-score", "subscore",
            "overall score", "dimension", "viability score"
        ],
        "market": [
            "tam", "sam", "som", "cagr", "persona", "market size", "target market",
            "audience", "customer", "demographic", "demand", "buyer", "addressable",
            "market", "industry", "segment", "opportunity"
        ]
    }

    WEB_SEARCH_TRIGGERS: List[str] = [
        "current", "latest", "recent", "today", "now", "news", "trends",
        "current pricing", "competitor pricing", "current competitors",
        "latest competitors", "recent funding", "recent regulation",
        "current regulation", "external company", "pricing of",
        "latest market", "market news", "industry news", "search the web",
        "search web", "in 2025", "in 2026", "right now", "real-world pricing"
    ]

    SHORT_FOLLOWUP_INDICATORS: List[str] = [
        "how can i reduce", "how to reduce", "why is that", "tell me more about",
        "can we lower that", "how to fix", "what else", "explain further",
        "why is it", "how to address", "what would make it", "how can we",
        "what should we", "how do we", "can we improve", "what about that",
        "which one first", "why is this", "how to overcome"
    ]

    def __init__(self, tavily_tool=None, model_name=None):
        super().__init__(model_name=model_name)
        self.tavily_tool = tavily_tool or TavilySearchTool()

    def _detect_explicit_intent(self, q_lower: str) -> Optional[str]:
        """Detects if a user question explicitly specifies a domain intent."""
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(kw in q_lower for kw in keywords):
                return intent
        return None

    def _get_previous_intent(self, chat_history: List[Dict[str, Any]]) -> Optional[str]:
        """Scans chat history backwards to find the most recent explicitly resolved intent."""
        for msg in reversed(chat_history):
            if msg.get("role") in ["user", "assistant"]:
                content = msg.get("content", "").lower().strip()
                intent = self._detect_explicit_intent(content)
                if intent:
                    return intent
        return None

    def classify_intent(self, user_question: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """Classifies user query intent deterministically using keyword rules and previous intent inheritance."""
        q_lower = user_question.lower().strip()

        # Step 1: Check if current question explicitly introduces a new topic / intent
        explicit_intent = self._detect_explicit_intent(q_lower)
        if explicit_intent:
            return explicit_intent

        # Step 2: Inherit previous resolved intent from chat history for follow-up questions
        if chat_history:
            prev_intent = self._get_previous_intent(chat_history)
            if prev_intent:
                logger.info(f"Inheriting previous intent '{prev_intent}' for follow-up question: '{user_question}'")
                return prev_intent

        return "general"

    def build_intent_context(self, intent: str, state: StartupState) -> str:
        """Constructs focused, intent-specific report context from StartupState."""
        report = state.final_report
        idea = state.idea
        sections = [
            f"Startup Concept: {idea.idea_text}",
            f"Industry: {idea.target_industry} | Target Audience: {idea.target_audience} | Business Model: {idea.business_model}",
            f"Overall Viability Score: {report.overall_viability_score}/100 | Verdict: {report.verdict}"
        ]

        if intent == "market":
            sections.append(f"Market Score: {report.market_score}/100")
            if state.market_analysis:
                m = state.market_analysis
                sections.append(f"Market Sizing: TAM=${m.tam_billions}B, SAM=${m.sam_billions}B, SOM=${m.som_billions}B, CAGR={m.cagr_percentage}%")
                sections.append(f"Market Summary: {m.market_size_summary}")
                if m.key_growth_drivers:
                    sections.append(f"Key Growth Drivers: {', '.join(m.key_growth_drivers)}")
                if m.target_personas:
                    persona_str = "; ".join(
                        f"{p.role} (Pain: {', '.join(p.pain_points)}, WTP: {p.willingness_to_pay})"
                        for p in m.target_personas
                    )
                    sections.append(f"Target Personas: {persona_str}")
            else:
                sections.append("Market Analysis: Detailed market data unavailable in report state.")

        elif intent == "competition":
            sections.append(f"Competitor Score: {report.competitor_score}/100")
            if state.structured_concept:
                if state.structured_concept.unique_value_prop:
                    sections.append(f"UVP: {state.structured_concept.unique_value_prop}")
                if state.structured_concept.competitive_advantage:
                    sections.append(f"Competitive Advantage: {state.structured_concept.competitive_advantage}")
            if state.competitor_analysis:
                c = state.competitor_analysis
                sections.append(f"Moat Assessment: {c.moat_assessment}")
                sections.append(f"Market Positioning: {c.market_positioning_summary}")
                direct_comps = [getattr(item, 'name', str(item)) for item in c.direct_competitors] if c.direct_competitors else []
                if direct_comps:
                    sections.append(f"Direct Competitors: {', '.join(direct_comps)}")
                indirect_comps = [getattr(item, 'name', str(item)) for item in c.indirect_competitors] if c.indirect_competitors else []
                if indirect_comps:
                    sections.append(f"Indirect Competitors: {', '.join(indirect_comps)}")
            else:
                sections.append("Competitor Analysis: Detailed competitor data unavailable in report state.")

        elif intent == "risk":
            sections.append(f"Risk Score: {report.risk_score}/100")
            if state.swot_analysis:
                s = state.swot_analysis
                sections.append(f"Risk Levels: Overall={s.overall_risk_score}/10, Financial={s.financial_risk}/10, Technical={s.technical_risk}/10, Regulatory={s.regulatory_risk}/10")
                if s.strengths:
                    sections.append(f"Strengths: {', '.join(s.strengths)}")
                if s.weaknesses:
                    sections.append(f"Weaknesses: {', '.join(s.weaknesses)}")
                if s.opportunities:
                    sections.append(f"Opportunities: {', '.join(s.opportunities)}")
                if s.threats:
                    sections.append(f"Threats: {', '.join(s.threats)}")
                if s.risk_mitigation_plan:
                    sections.append(f"Risk Mitigation Plan: {'; '.join(s.risk_mitigation_plan)}")
                if s.risk_matrix:
                    matrix_items = [f"{r.risk_name} ({r.category}, Sev:{r.severity_score}): {r.mitigation_strategy}" for r in s.risk_matrix]
                    sections.append(f"Risk Matrix Items: {'; '.join(matrix_items)}")
            else:
                sections.append("SWOT/Risk Analysis: Detailed risk data unavailable in report state.")

        elif intent == "mvp":
            sections.append(f"MVP Score: {report.mvp_score}/100")
            if state.mvp_recommendation:
                mvp = state.mvp_recommendation
                sections.append(f"Core Value Proposition: {mvp.core_value_proposition}")
                sections.append(f"Tech Stack: Frontend ({mvp.tech_stack_frontend}), Backend ({mvp.tech_stack_backend}), Database ({mvp.tech_stack_database}), AI ({mvp.tech_stack_ai})")
                if mvp.features:
                    feat_str = "; ".join(f"{f.feature_name} [{f.priority}, ~{f.estimated_days}d]: {f.description}" for f in mvp.features)
                    sections.append(f"MVP Features: {feat_str}")
                if mvp.four_week_roadmap:
                    roadmap_str = "; ".join(f"{w}: {task}" for w, task in mvp.four_week_roadmap.items())
                    sections.append(f"4-Week Roadmap: {roadmap_str}")
                if mvp.key_metrics_kpis:
                    sections.append(f"Key Metrics & KPIs: {', '.join(mvp.key_metrics_kpis)}")
            else:
                sections.append("MVP Recommendation: Detailed MVP data unavailable in report state.")

        elif intent == "gtm":
            sections.append(f"GTM Score: {report.gtm_score}/100")
            if state.gtm_strategy:
                gtm = state.gtm_strategy
                if gtm.primary_acquisition_channels:
                    sections.append(f"Primary Channels: {', '.join(gtm.primary_acquisition_channels)}")
                sections.append(f"Pricing Strategy: {gtm.pricing_strategy}")
                sections.append(f"Positioning Statement: {gtm.positioning_statement}")
                if gtm.launch_tactics:
                    sections.append(f"Launch Tactics: {', '.join(gtm.launch_tactics)}")
                sections.append(f"CAC Summary: {gtm.estimated_cac_summary}")
            else:
                sections.append("GTM Strategy: Detailed GTM data unavailable in report state.")

        elif intent == "score":
            sections.append(f"Overall Viability Score: {report.overall_viability_score}/100 (Verdict: {report.verdict})")
            sections.append(f"Executive Summary: {report.executive_summary}")
            sections.append(f"Sub-Scores: Market={report.market_score}, Competitor={report.competitor_score}, Risk={report.risk_score}, MVP={report.mvp_score}, GTM={report.gtm_score}")
            sections.append(f"Investor Readiness={getattr(report, 'investor_readiness_score', 75)}/100, Funding Probability={getattr(report, 'funding_probability', 65)}%, PMF={getattr(report, 'pmf_score', 70)}, Confidence={getattr(report, 'confidence_score', 85)}")
            if getattr(report, "scoring_breakdown", None):
                sb = report.scoring_breakdown
                reasoning = getattr(sb, "reasoning_why", [])
                if reasoning:
                    sections.append(f"Explainable Deductions: {', '.join(reasoning)}")
            if getattr(report, "key_takeaways", None):
                sections.append(f"Key Takeaways: {', '.join(report.key_takeaways)}")

        elif intent == "funding":
            sections.append(f"Investor Readiness Score: {report.investor_readiness_score}/100")
            sections.append(f"Funding Probability: {report.funding_probability}%")
            sections.append(f"Product-Market Fit Score: {report.pmf_score}/100")
            sections.append(f"Confidence Score: {report.confidence_score}/100")
            if report.recommended_next_steps:
                sections.append(f"Recommended Next Steps: {', '.join(report.recommended_next_steps)}")
            if state.swot_analysis:
                risks = (state.swot_analysis.weaknesses or []) + (state.swot_analysis.threats or [])
                if risks:
                    sections.append(f"Top Risk Considerations: {', '.join(risks)}")

        else:  # general
            sections.append(f"Executive Summary: {report.executive_summary}")
            sections.append(f"Sub-Scores: Market={report.market_score}, Competitor={report.competitor_score}, Risk={report.risk_score}, MVP={report.mvp_score}, GTM={report.gtm_score}")
            sections.append(f"Investor Readiness={getattr(report, 'investor_readiness_score', 75)}/100 | Funding Probability={getattr(report, 'funding_probability', 65)}%")
            if getattr(report, "key_takeaways", None):
                sections.append(f"Key Takeaways: {', '.join(report.key_takeaways)}")
            if getattr(report, "recommended_next_steps", None):
                sections.append(f"Recommended Next Steps: {', '.join(report.recommended_next_steps)}")

        return "\n".join(sections)

    def should_search_web(
        self,
        user_question: str,
        intent: str,
        report_context: str
    ) -> bool:
        """Determines whether web research is required for the user's question."""
        q_lower = user_question.lower().strip()

        # 1. Direct questions about report metrics NEVER trigger web search
        report_internal_questions = [
            "viability score", "overall score", "my score", "investor readiness",
            "biggest risk", "weakness", "strengths", "swot", "mvp tech stack",
            "mvp features", "tam", "sam", "som", "gtm channel", "acquisition channel",
            "verdict", "next steps", "key takeaways", "confidence score", "pmf score"
        ]
        if any(term in q_lower for term in report_internal_questions):
            return False

        # 2. Short follow-up questions inherit domain intent and do not require web search
        if any(q_lower.startswith(prefix) for prefix in self.SHORT_FOLLOWUP_INDICATORS):
            return False

        # 3. Explicit triggers for current information, pricing, news, or external companies
        if any(trigger in q_lower for trigger in self.WEB_SEARCH_TRIGGERS):
            return True

        # 4. Check if current domain data is completely missing in report context
        domain_missing_indicators = {
            "market": "Market Analysis: Detailed market data unavailable",
            "competition": "Competitor Analysis: Detailed competitor data unavailable",
            "risk": "SWOT/Risk Analysis: Detailed risk data unavailable",
            "mvp": "MVP Recommendation: Detailed MVP data unavailable",
            "gtm": "GTM Strategy: Detailed GTM data unavailable",
        }
        if intent in domain_missing_indicators:
            if domain_missing_indicators[intent] in report_context:
                return True

        return False

    def search_web_for_advisor(
        self,
        user_question: str,
        state: StartupState,
        intent: str
    ) -> List[Dict[str, Any]]:
        """Constructs a focused, domain-specific search query and executes Tavily search."""
        idea_text = state.idea.idea_text if state and state.idea else ""
        industry = state.idea.target_industry if state and state.idea else ""

        # Construct safe, focused query
        query = f'"{idea_text}" {industry} {intent} {user_question}'.strip()
        logger.info(f"ConversationalAdvisor executing Tavily search with query: '{query}'")

        try:
            results = self.tavily_tool.search(query=query, max_results=5)
            if isinstance(results, list):
                return results
            return []
        except Exception as e:
            logger.warning(f"ConversationalAdvisor Tavily search failed gracefully: {e}")
            return []

    def format_web_evidence(
        self,
        results: List[Dict[str, Any]]
    ) -> str:
        """Formats web research results for inclusion in LLM prompt."""
        if not results:
            return "No web research evidence available."

        lines = ["WEB RESEARCH RESULTS:"]
        for idx, item in enumerate(results, 1):
            title = item.get("title", "Untitled Web Result")
            url = item.get("url", "")
            snippet = item.get("snippet", "") or item.get("content", "")
            lines.append(f"{idx}. {title}\n   URL: {url}\n   Evidence: {snippet}")

        return "\n".join(lines)

    def generate_grounded_fallback(
        self,
        user_question: str,
        intent: str,
        state: StartupState,
        web_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generates an intent-aware, structured grounded response when LLMService is unavailable."""
        report = state.final_report
        idea = state.idea
        q_lower = user_question.lower().strip()

        # Detect action vs fact questions
        is_action_question = any(kw in q_lower for kw in [
            "how", "reduce", "mitigate", "action", "decrease", "address", "solve",
            "overcome", "tackle", "lower", "minimize", "prevent", "avoid", "improve",
            "fix", "step", "strategy", "plan", "execute", "build", "acquire", "cut"
        ])

        # Handle unanswerable / unrelated questions when report evidence is not present
        report_related_keywords = [
            "summary", "report", "overview", "startup", "idea", "verdict",
            "score", "takeaway", "next step", "recommendation", "viability",
            "overall", "market", "risk", "competitor", "mvp", "gtm", "funding", "investor"
        ]
        if intent == "general" and not any(kw in q_lower for kw in report_related_keywords) and not web_results:
            return "The validation report does not contain enough evidence to answer this question."

        direct_answer = ""
        why_it_matters = ""
        recommended_action = ""
        evidence = ""

        if intent == "risk":
            if state.swot_analysis and (state.swot_analysis.weaknesses or state.swot_analysis.risk_matrix):
                top_risk = state.swot_analysis.weaknesses[0] if state.swot_analysis.weaknesses else "Execution and budget risk"
                overall_lvl = state.swot_analysis.overall_risk_score

                if is_action_question:
                    # Action / Mitigation response
                    mitigations = []
                    if state.swot_analysis.risk_mitigation_plan:
                        mitigations.extend(state.swot_analysis.risk_mitigation_plan)
                    if state.swot_analysis.risk_matrix:
                        for rm in state.swot_analysis.risk_matrix:
                            if rm.mitigation_strategy and rm.mitigation_strategy not in mitigations:
                                mitigations.append(rm.mitigation_strategy)

                    mitigation_summary = "; ".join(mitigations[:2]) if mitigations else f"Implement phased testing milestones and clear operational spend limits to de-risk '{top_risk}'."
                    direct_answer = f"To reduce and mitigate the primary risk of **'{top_risk}'**, implement the following concrete actions: **{mitigation_summary}**."
                    why_it_matters = f"Proactive risk mitigation safeguards runway, reduces operational friction, and directly improves your Risk Score ({report.risk_score}/100) and Investor Readiness ({report.investor_readiness_score}/100)."
                    action_steps = [f"{i+1}. {m}" for i, m in enumerate(mitigations[:3])] if mitigations else [f"1. Establish technical safeguards against '{top_risk}'.", "2. Monitor unit economics before scaling customer acquisition."]
                    recommended_action = "\n".join(action_steps)
                    evidence = f"Identified Weakness: {top_risk} | Overall Risk Level: {overall_lvl}/10 | Mitigations: {', '.join(mitigations or ['Phased validation'])}"
                else:
                    # Fact response
                    direct_answer = f"The primary identified risk for **'{idea.idea_text}'** is: **{top_risk}**."
                    why_it_matters = f"This vulnerability is the primary factor in your Risk Score ({report.risk_score}/100) and overall viability assessment ({report.overall_viability_score}/100)."
                    recommended_action = f"De-risk '{top_risk}' in your initial MVP milestone before investing in broad customer acquisition."
                    evidence = f"Overall Risk Score: {report.risk_score}/100 | Risk Level: {overall_lvl}/10 | Weaknesses: {', '.join(state.swot_analysis.weaknesses)}"
            else:
                return "The validation report does not contain enough evidence to detail specific risk mitigations."

        elif intent == "market":
            if state.market_analysis:
                m = state.market_analysis
                direct_answer = f"The estimated Total Addressable Market (TAM) is **${m.tam_billions}B** with SAM of **${m.sam_billions}B** and SOM of **${m.som_billions}B** (CAGR: {m.cagr_percentage}%)."
                why_it_matters = f"A robust market sizing validates long-term revenue potential for {idea.target_industry} investors."
                recommended_action = "Target early-adopter SOM segments before scaling out to broader SAM audience."
                evidence = f"TAM=${m.tam_billions}B, SAM=${m.sam_billions}B, SOM=${m.som_billions}B | Market Score: {report.market_score}/100"
            else:
                return "The validation report does not contain enough evidence to provide detailed market metrics."

        elif intent == "competition":
            if web_results:
                # Primary evidence from web research for current competitor findings
                comp_entries = []
                for res in web_results:
                    title = res.get("title", "").strip()
                    snippet = (res.get("snippet") or res.get("content") or "").strip()
                    if title:
                        summary_snippet = snippet[:160] + "..." if len(snippet) > 160 else snippet
                        comp_entries.append(f"- **{title}**: {summary_snippet}" if summary_snippet else f"- **{title}**")

                if comp_entries:
                    comp_text = "\n".join(comp_entries[:3])
                    direct_answer = (
                        f"Based on current market research for **'{idea.target_industry}'**, key active market solutions and emerging competitors include:\n\n"
                        f"{comp_text}"
                    )
                else:
                    direct_answer = "Current web research did not provide enough reliable evidence to identify specific competitors."

                why_it_matters = f"Active market alternatives create direct pricing and feature comparison points for {idea.target_industry} buyers."
                moat = state.competitor_analysis.moat_assessment if (state.competitor_analysis and state.competitor_analysis.moat_assessment) else "specialized niche positioning and faster workflow automation"
                recommended_action = f"Differentiate by sharpening your primary moat: **{moat}**."
                evidence = f"Validation Report Competitor Score: {report.competitor_score}/100 | Target Moat: {moat}"
            elif state.competitor_analysis and state.competitor_analysis.moat_assessment:
                c = state.competitor_analysis
                direct_answer = f"Your competitive positioning focuses on: **{c.market_positioning_summary or c.moat_assessment}**."
                why_it_matters = "Defensible differentiation creates a moat against existing market players."
                recommended_action = f"Focus MVP on core differentiator: {c.moat_assessment}"
                evidence = f"Moat Assessment: {c.moat_assessment} | Competitor Score: {report.competitor_score}/100"
            else:
                return "The validation report does not contain enough evidence to analyze competitor dynamics."

        elif intent == "mvp":
            if state.mvp_recommendation:
                mvp = state.mvp_recommendation
                direct_answer = f"The recommended MVP tech stack relies on **{mvp.tech_stack_frontend}** (Frontend), **{mvp.tech_stack_backend}** (Backend), and **{mvp.tech_stack_ai}** (AI)."
                why_it_matters = "Choosing a lean tech stack enables rapid validation within budget constraints."
                top_feats = [f.feature_name for f in mvp.features[:2]] if mvp.features else ['Core workflow']
                recommended_action = f"Focus initial build on top priority features: {', '.join(top_feats)}"
                evidence = f"MVP Score: {report.mvp_score}/100 | Core Value Prop: {mvp.core_value_proposition}"
            else:
                return "The validation report does not contain enough evidence to provide MVP specifications."

        elif intent == "gtm":
            if state.gtm_strategy:
                gtm = state.gtm_strategy
                direct_answer = f"Primary customer acquisition channels: **{', '.join(gtm.primary_acquisition_channels)}**."
                why_it_matters = "Channel alignment is critical for achieving sustainable Customer Acquisition Cost (CAC)."
                tactics = gtm.launch_tactics[:2] if gtm.launch_tactics else ['Direct outreach']
                recommended_action = f"Execute launch tactics: {', '.join(tactics)}"
                evidence = f"GTM Score: {report.gtm_score}/100 | Pricing: {gtm.pricing_strategy}"
            else:
                return "The validation report does not contain enough evidence to detail GTM channels."

        elif intent == "score":
            direct_answer = f"Your Overall Viability Score is **{report.overall_viability_score}/100** with a strategic verdict of **{report.verdict}**."
            why_it_matters = f"This score combines deterministic evaluations across Market ({report.market_score}/100), Competitor ({report.competitor_score}/100), Risk ({report.risk_score}/100), MVP ({report.mvp_score}/100), and GTM ({report.gtm_score}/100)."
            next_step = report.recommended_next_steps[0] if (report.recommended_next_steps) else 'Address top weaknesses and build core MVP'
            recommended_action = f"Primary Next Step: {next_step}"
            sb = getattr(report, "scoring_breakdown", None)
            deductions = getattr(sb, "reasoning_why", []) if sb else []
            deductions_str = f" | Deductions: {', '.join(deductions)}" if deductions else ""
            evidence = f"Market: {report.market_score}, Competitor: {report.competitor_score}, Risk: {report.risk_score}, MVP: {report.mvp_score}, GTM: {report.gtm_score}{deductions_str}"

        elif intent == "funding":
            direct_answer = f"Your Investor Readiness Score is **{report.investor_readiness_score}/100** (Funding Probability: **{report.funding_probability}%**, PMF Score: **{report.pmf_score}/100**)."
            why_it_matters = "Investors evaluate PMF score and execution risk before committing capital."
            next_step = report.recommended_next_steps[0] if report.recommended_next_steps else 'Prepare pitch deck'
            recommended_action = f"Next Step: {next_step}"
            evidence = f"PMF Score: {report.pmf_score}/100 | Overall Viability Score: {report.overall_viability_score}/100 ({report.verdict})"

        else:
            direct_answer = f"Based on the validation report for **'{idea.idea_text}'** (Overall Viability: **{report.overall_viability_score}/100**, Verdict: **{report.verdict}**): {report.executive_summary}"
            why_it_matters = "Comprehensive validation helps de-risk early-stage startup execution."
            next_step = report.recommended_next_steps[0] if report.recommended_next_steps else 'Focus on MVP scoping'
            recommended_action = f"Recommended Next Step: {next_step}"
            takeaways = report.key_takeaways[:2] if report.key_takeaways else ['See full report']
            evidence = f"Executive Summary & Key Takeaways: {', '.join(takeaways)}"

        base_response = (
            f"### Direct Answer\n{direct_answer}\n\n"
            f"### Why It Matters\n{why_it_matters}\n\n"
            f"### Recommended Action\n{recommended_action}\n\n"
            f"### Evidence From Validation\n{evidence}"
        )

        if web_results:
            sources_list = "\n".join(
                f"- [{res.get('title', 'Web Source')}] — {res.get('url', '')}"
                for res in web_results if res.get('url')
            )
            if sources_list:
                base_response += f"\n\n### Additional Web Research\n{sources_list}"

        return base_response

    def answer_question(
        self,
        user_question: str,
        state: StartupState,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Answers user question using report-first context, intent classification, Tavily web search fallback, and Gemini synthesis."""
        logger.info(f"ConversationalAdvisor answering user question: '{user_question}'")
        try:
            # A. Validate state and final report
            if not state or not state.final_report:
                return "No validation report data is available for this session. Please validate a startup concept first."

            # B. Detect intent
            intent = self.classify_intent(user_question, chat_history)
            logger.info(f"ConversationalAdvisor query intent classified as: '{intent}'")

            # C. Build intent-specific report context
            report_context = self.build_intent_context(intent, state)

            # D. Build bounded chat history summary
            history_str = "None"
            if chat_history:
                recent_msgs = chat_history[-6:]
                if recent_msgs and recent_msgs[-1].get("role") == "user" and recent_msgs[-1].get("content") == user_question:
                    recent_msgs = recent_msgs[:-1]
                if recent_msgs:
                    history_lines = [f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in recent_msgs]
                    history_str = "\n".join(history_lines)

            # E. Determine whether web research is needed
            needs_web = self.should_search_web(user_question, intent, report_context)
            web_results = []
            web_context = "None"

            if needs_web:
                logger.info(f"ConversationalAdvisor requiring web research for question: '{user_question}'")
                web_results = self.search_web_for_advisor(user_question, state, intent)
                web_context = self.format_web_evidence(web_results)

            # Prepare prompt
            prompt = self.load_prompt(
                "advisor_agent",
                intent=intent,
                report_context=report_context,
                web_research_context=web_context,
                chat_history_summary=history_str,
                user_question=user_question
            )

            # F & G. Call Gemini LLM
            text_response = self.generate_text(
                prompt,
                system_instruction="You are an expert venture capital strategic advisor."
            )

            if text_response:
                # If web research was performed and results exist, ensure web sources attribution section is present
                if needs_web and web_results and "### Additional Web Research" not in text_response:
                    sources_list = "\n".join(
                        f"- [{res.get('title', 'Web Source')}] — {res.get('url', '')}"
                        for res in web_results if res.get('url')
                    )
                    if sources_list:
                        text_response += f"\n\n### Additional Web Research\n{sources_list}"
                return text_response

            # H. Grounded Fallback when LLM text generation is unavailable
            logger.info("LLM text generation unavailable. Generating fallback response.")

            if not needs_web:
                return self.generate_grounded_fallback(user_question, intent, state)

            if web_results:
                return self.generate_grounded_fallback(user_question, intent, state, web_results=web_results)

            return "External web research is currently unavailable. I can still answer using your validation report."

        except Exception as e:
            logger.error(f"Error in ConversationalAdvisor: {e}", exc_info=True)
            return f"An error occurred while consulting the AI Advisor: {str(e)}"
