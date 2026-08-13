import logging
from typing import List, Dict, Optional, Any
from agents.base_agent import BaseAgent
from state.schema import StartupState
from services.logger import get_logger

logger = get_logger(__name__)


class ConversationalAdvisor(BaseAgent):
    """Grounded Strategic Venture Advisor Q&A Agent answering follow-up questions exclusively from generated report evidence."""

    INTENT_KEYWORDS: Dict[str, List[str]] = {
        "risk": ["risk", "swot", "threat", "weakness", "mitigat", "vulnerability", "hazard", "pitfall", "downside", "fail", "financial risk", "technical risk", "regulatory risk", "severity"],
        "competition": ["competitor", "competition", "moat", "differentiate", "positioning", "alternative", "rival", "substitute", "landscape", "matrix", "advantage", "benchmark"],
        "mvp": ["mvp", "prototype", "feature", "tech stack", "roadmap", "build", "frontend", "backend", "database", "kpi", "launch date", "timeline", "architecture", "product", "minimum viable"],
        "gtm": ["gtm", "go-to-market", "go to market", "channel", "acquisition", "cac", "pricing", "monetiz", "sales", "launch tactic", "marketing"],
        "funding": ["fund", "investor", "readiness", "pmf", "pitch", "raise", "capital", "venture", "vc", "probability", "seed", "angel", "product-market fit", "product market fit"],
        "score": ["score", "viability", "breakdown", "verdict", "rating", "evaluate", "metric", "grade", "reasoning", "points"],
        "market": ["tam", "sam", "som", "cagr", "persona", "market size", "target market", "audience", "customer", "demographic", "demand", "buyer", "addressable", "market"]
    }

    def _detect_explicit_intent(self, q_lower: str) -> Optional[str]:
        """Detects if a user question explicitly specifies a domain intent."""
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(kw in q_lower for kw in keywords):
                return intent
        return None

    def _get_previous_intent(self, chat_history: List[Dict[str, str]]) -> Optional[str]:
        """Scans chat history backwards to find the most recent explicitly resolved intent."""
        for msg in reversed(chat_history):
            if msg.get("role") == "user":
                content = msg.get("content", "").lower().strip()
                intent = self._detect_explicit_intent(content)
                if intent:
                    return intent
        return None

    def classify_intent(self, user_question: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
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
                    persona_str = "; ".join(f"{p.role} (Pain: {', '.join(p.pain_points)}, WTP: {p.willingness_to_pay})" for p in m.target_personas)
                    sections.append(f"Target Personas: {persona_str}")
            else:
                sections.append("Market Analysis: Detailed market data unavailable in report state.")

        elif intent == "competition":
            sections.append(f"Competitor Score: {report.competitor_score}/100")
            if state.structured_concept:
                sections.append(f"UVP: {state.structured_concept.unique_value_prop}")
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
                sections.append(f"Strengths: {', '.join(s.strengths)}")
                sections.append(f"Weaknesses: {', '.join(s.weaknesses)}")
                sections.append(f"Opportunities: {', '.join(s.opportunities)}")
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
                sections.append(f"Primary Channels: {', '.join(gtm.primary_acquisition_channels)}")
                sections.append(f"Pricing Strategy: {gtm.pricing_strategy}")
                sections.append(f"Positioning Statement: {gtm.positioning_statement}")
                sections.append(f"Launch Tactics: {', '.join(gtm.launch_tactics)}")
                sections.append(f"CAC Summary: {gtm.estimated_cac_summary}")
            else:
                sections.append("GTM Strategy: Detailed GTM data unavailable in report state.")

        elif intent == "score":
            sections.append(f"Executive Summary: {report.executive_summary}")
            sections.append(f"Sub-Scores: Market={report.market_score}, Competitor={report.competitor_score}, Risk={report.risk_score}, MVP={report.mvp_score}, GTM={report.gtm_score}")
            sections.append(f"Investor Readiness={report.investor_readiness_score}, Funding Probability={report.funding_probability}%, PMF={report.pmf_score}, Confidence={report.confidence_score}")
            if report.scoring_breakdown:
                sb = report.scoring_breakdown
                sections.append(f"Explainable Deductions: {', '.join(sb.reasoning_why)}")
                sections.append(f"Calculation Methodology: {', '.join(sb.reasoning_how)}")
            sections.append(f"Key Takeaways: {', '.join(report.key_takeaways)}")

        elif intent == "funding":
            sections.append(f"Investor Readiness Score: {report.investor_readiness_score}/100")
            sections.append(f"Funding Probability: {report.funding_probability}%")
            sections.append(f"Product-Market Fit Score: {report.pmf_score}/100")
            sections.append(f"Confidence Score: {report.confidence_score}/100")
            sections.append(f"Recommended Next Steps: {', '.join(report.recommended_next_steps)}")
            if state.swot_analysis:
                sections.append(f"Top Risk Considerations: {', '.join(state.swot_analysis.weaknesses + state.swot_analysis.threats)}")

        else:  # general
            sections.append(f"Executive Summary: {report.executive_summary}")
            sections.append(f"Sub-Scores: Market={report.market_score}, Competitor={report.competitor_score}, Risk={report.risk_score}, MVP={report.mvp_score}, GTM={report.gtm_score}")
            sections.append(f"Investor Readiness={report.investor_readiness_score}/100 | Funding Probability={report.funding_probability}%")
            sections.append(f"Key Takeaways: {', '.join(report.key_takeaways)}")
            sections.append(f"Recommended Next Steps: {', '.join(report.recommended_next_steps)}")

        return "\n".join(sections)

    def generate_grounded_fallback(self, user_question: str, intent: str, state: StartupState) -> str:
        """Generates an intent-aware, structured grounded response when LLMService is unavailable."""
        report = state.final_report
        idea = state.idea

        # Handle unanswerable / unrelated questions when report evidence is not present or asked for
        report_related_keywords = ["summary", "report", "overview", "startup", "idea", "verdict", "score", "takeaway", "next step", "recommendation", "viability", "overall"]
        if intent == "general" and not any(kw in user_question.lower() for kw in report_related_keywords):
            return "The validation report does not contain enough evidence to answer this question."

        direct_answer = ""
        why_it_matters = ""
        recommended_action = ""
        evidence = ""

        if intent == "risk":
            if state.swot_analysis and (state.swot_analysis.weaknesses or state.swot_analysis.risk_matrix):
                top_risk = state.swot_analysis.weaknesses[0] if state.swot_analysis.weaknesses else "Execution and market risk"
                direct_answer = f"The primary identified risk for **'{idea.idea_text}'** is: {top_risk}."
                why_it_matters = f"Risk mitigation directly affects your Risk Score ({report.risk_score}/100) and overall viability score ({report.overall_viability_score}/100)."
                recommended_action = state.swot_analysis.risk_mitigation_plan[0] if state.swot_analysis.risk_mitigation_plan else "Implement phased risk testing before launching full GTM."
                evidence = f"Overall Risk Level: {state.swot_analysis.overall_risk_score}/10 | Weaknesses: {', '.join(state.swot_analysis.weaknesses)}"
            else:
                return "The validation report does not contain enough evidence to detail specific risk mitigations."

        elif intent == "market":
            if state.market_analysis:
                m = state.market_analysis
                direct_answer = f"The estimated Total Addressable Market (TAM) is **${m.tam_billions}B** with SAM of **${m.sam_billions}B** (CAGR: {m.cagr_percentage}%)."
                why_it_matters = f"A robust market sizing validates long-term revenue potential for {idea.target_industry} investors."
                recommended_action = "Target early-adopter SOM segments before scaling out to broader SAM audience."
                evidence = f"TAM=${m.tam_billions}B, SAM=${m.sam_billions}B, SOM=${m.som_billions}B | Market Score: {report.market_score}/100"
            else:
                return "The validation report does not contain enough evidence to provide detailed market metrics."

        elif intent == "competition":
            if state.competitor_analysis and state.competitor_analysis.moat_assessment:
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
                recommended_action = f"Focus initial build on top priority features: {', '.join([f.feature_name for f in mvp.features[:2]]) if mvp.features else 'Core workflow'}"
                evidence = f"MVP Score: {report.mvp_score}/100 | Core Value Prop: {mvp.core_value_proposition}"
            else:
                return "The validation report does not contain enough evidence to provide MVP specifications."

        elif intent == "gtm":
            if state.gtm_strategy:
                gtm = state.gtm_strategy
                direct_answer = f"Primary customer acquisition channels: **{', '.join(gtm.primary_acquisition_channels)}**."
                why_it_matters = f"Channel alignment is critical for achieving sustainable Customer Acquisition Cost (CAC)."
                recommended_action = f"Execute launch tactics: {', '.join(gtm.launch_tactics[:2]) if gtm.launch_tactics else 'Direct outreach'}"
                evidence = f"GTM Score: {report.gtm_score}/100 | Pricing: {gtm.pricing_strategy}"
            else:
                return "The validation report does not contain enough evidence to detail GTM channels."

        elif intent == "score":
            direct_answer = f"Overall Viability Score is **{report.overall_viability_score}/100** with a strategic verdict of **{report.verdict}**."
            why_it_matters = "The score reflects deterministic evaluation across market, competitor, risk, MVP, and GTM dimensions."
            recommended_action = f"Primary recommendation: {report.recommended_next_steps[0] if report.recommended_next_steps else 'Address identified weaknesses'}"
            evidence = f"Market: {report.market_score}, Competitor: {report.competitor_score}, Risk: {report.risk_score}, MVP: {report.mvp_score}, GTM: {report.gtm_score}"

        elif intent == "funding":
            direct_answer = f"Investor Readiness Score is **{report.investor_readiness_score}/100** (Funding Probability: **{report.funding_probability}%**)."
            why_it_matters = "Investors evaluate PMF score and execution risk before committing capital."
            recommended_action = f"Next Step: {report.recommended_next_steps[0] if report.recommended_next_steps else 'Prepare pitch deck'}"
            evidence = f"PMF Score: {report.pmf_score}/100 | Overall Viability Score: {report.overall_viability_score}/100 ({report.verdict})"

        else:
            direct_answer = f"Based on the validation report for **'{idea.idea_text}'** (Overall Viability: **{report.overall_viability_score}/100**, Verdict: **{report.verdict}**): {report.executive_summary}"
            why_it_matters = "Comprehensive validation helps de-risk early-stage startup execution."
            recommended_action = f"Recommended Next Step: {report.recommended_next_steps[0] if report.recommended_next_steps else 'Focus on MVP scoping'}"
            evidence = f"Executive Summary & Key Takeaways: {', '.join(report.key_takeaways[:2]) if report.key_takeaways else 'See full report'}"

        return (
            f"### Direct Answer\n{direct_answer}\n\n"
            f"### Why It Matters\n{why_it_matters}\n\n"
            f"### Recommended Action\n{recommended_action}\n\n"
            f"### Evidence From Validation\n{evidence}"
        )

    def answer_question(self, user_question: str, state: StartupState, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Answers user question using intent classification, context selection, and Gemini LLM with grounded fallback."""
        logger.info(f"ConversationalAdvisor answering user question: '{user_question}'")
        try:
            if not state or not state.final_report:
                return "No validation report data is available for this session. Please validate a startup concept first."

            intent = self.classify_intent(user_question, chat_history)
            logger.info(f"ConversationalAdvisor query intent classified as: '{intent}'")

            report_context = self.build_intent_context(intent, state)

            # Bounded recent history window (last 6 messages / 3 turns)
            history_str = "None"
            if chat_history:
                recent_msgs = chat_history[-6:]
                # Filter out exact current question if present at the end
                if recent_msgs and recent_msgs[-1].get("role") == "user" and recent_msgs[-1].get("content") == user_question:
                    recent_msgs = recent_msgs[:-1]
                if recent_msgs:
                    history_lines = [f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in recent_msgs]
                    history_str = "\n".join(history_lines)

            prompt = self.load_prompt(
                "advisor_agent",
                intent=intent,
                report_context=report_context,
                chat_history_summary=history_str,
                user_question=user_question
            )

            text_response = self.generate_text(
                prompt,
                system_instruction="You are an expert venture capital strategic advisor."
            )

            if text_response:
                return text_response

            # Heuristic grounded fallback when LLMService returns None
            logger.info("LLM text generation unavailable. Using grounded intent-aware fallback.")
            return self.generate_grounded_fallback(user_question, intent, state)

        except Exception as e:
            logger.error(f"Error in ConversationalAdvisor: {e}", exc_info=True)
            return f"An error occurred while consulting the AI Advisor: {str(e)}"
