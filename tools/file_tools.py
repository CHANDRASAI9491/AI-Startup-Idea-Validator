import os
import json
import logging
from typing import Dict, Any, Optional
from state.schema import StartupState

logger = logging.getLogger(__name__)


class FileTools:
    """Utility functions for exporting reports in Markdown, JSON, and PDF formats."""

    @staticmethod
    def export_report_markdown(state: StartupState, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        report = state.final_report
        idea = state.idea
        market = state.market_analysis
        comp = state.competitor_analysis
        swot = state.swot_analysis
        mvp = state.mvp_recommendation
        gtm = state.gtm_strategy
        plan = state.planning_output
        scoring = report.scoring_breakdown if report else None

        lines = [
            f"# Executive Startup Validation & Decision Support Report",
            f"**Concept Description:** {idea.idea_text}",
            f"**Generated Date:** {report.timestamp if report else 'N/A'}",
            f"**Industry Sector:** {idea.target_industry} | **Target Market:** {idea.target_audience} | **Business Model:** {idea.business_model}",
            "\n---",
            "## Executive Summary & Investor Metrics",
            f"**Overall Viability Score:** {report.overall_viability_score}/100" if report else "",
            f"**Strategic Verdict:** {report.verdict}" if report else "",
            f"**Investor Readiness Score:** {report.investor_readiness_score}/100" if report else "",
            f"**Funding Probability:** {report.funding_probability}%" if report else "",
            f"**Product-Market Fit Score:** {report.pmf_score}/100" if report else "",
            f"\n{report.executive_summary if report else ''}",
        ]

        if scoring:
            lines.extend([
                "\n### 8-Dimension Weighted Score Breakdown Matrix",
                f"- **Market Opportunity:** {scoring.market_opportunity_score}/20",
                f"- **Innovation & Differentiation:** {scoring.innovation_score}/15",
                f"- **Competition & Defensible Moat:** {scoring.competition_score}/15",
                f"- **Scalability Potential:** {scoring.scalability_score}/15",
                f"- **Technical Feasibility:** {scoring.technical_feasibility_score}/10",
                f"- **Revenue Model Viability:** {scoring.revenue_model_score}/10",
                f"- **Execution & Risk Resilience:** {scoring.execution_risk_score}/10",
                f"- **Market Timing:** {scoring.market_timing_score}/5",
                f"\n**Total Viability Score:** {scoring.total_viability_score}/100",
                "\n### Explainable Reasoning (WHY):"
            ])
            for r in scoring.reasoning_why:
                lines.append(f"- {r}")

        if report:
            lines.append("\n### Key Takeaways")
            for t in report.key_takeaways:
                lines.append(f"- {t}")

            lines.append("\n### Recommended Next Steps")
            for step in report.recommended_next_steps:
                lines.append(f"1. {step}")

        if plan:
            lines.extend([
                "\n---",
                "## Strategic Execution Plan (DeepAgents)",
                f"**Strategic Objective:** {plan.strategic_objective}",
                "\n**Key Research Questions:**"
            ])
            for q in plan.research_questions:
                lines.append(f"- {q}")

        if market:
            tam_str = f"${market.tam_billions}B" if getattr(market, "tam_billions", None) is not None else "Evidence unavailable"
            sam_str = f"${market.sam_billions}B" if getattr(market, "sam_billions", None) is not None else "Evidence unavailable"
            som_str = f"${market.som_billions}B" if getattr(market, "som_billions", None) is not None else "Evidence unavailable"
            cagr_str = f"{market.cagr_percentage}%" if getattr(market, "cagr_percentage", None) is not None else "Evidence unavailable"
            readiness_str = f"{market.market_readiness_score}/100" if getattr(market, "market_readiness_score", None) is not None else "Evidence unavailable"
            lines.extend([
                "\n---",
                "## 1. Market Sizing and Growth Analysis",
                f"- **Total Addressable Market (TAM):** {tam_str}",
                f"- **Serviceable Addressable Market (SAM):** {sam_str}",
                f"- **Serviceable Obtainable Market (SOM):** {som_str}",
                f"- **Projected CAGR:** {cagr_str}",
                f"- **Market Readiness Score:** {readiness_str}",
                f"\n**Market Scope Summary:** {market.market_size_summary}",
                "\n**Primary Growth Drivers:**"
            ])
            if getattr(market, "key_growth_drivers", None):
                for driver in market.key_growth_drivers:
                    lines.append(f"- {driver}")
            else:
                lines.append("- No verified growth drivers established from available research.")

        if comp:
            lines.extend([
                "\n---",
                "## 2. Competitive Intelligence and Moat",
                f"**Market Positioning:** {comp.market_positioning_summary}",
                f"**Competitive Moat:** {comp.moat_assessment}",
                "\n### Direct Competitors:"
            ])
            if getattr(comp, "direct_competitors", None):
                for c in comp.direct_competitors:
                    pricing_str = f" ({c.pricing_model})" if getattr(c, "pricing_model", "").strip() else ""
                    lines.append(f"- **{c.name}**{pricing_str}: {c.description}")
            else:
                lines.append("- No verified competitors identified from available research.")

        if swot:
            lines.extend([
                "\n---",
                "## 3. SWOT Analysis and Risk Evaluation",
                f"- **Financial Risk Index:** {swot.financial_risk}/10",
                f"- **Technical Risk Index:** {swot.technical_risk}/10",
                f"- **Regulatory Risk Index:** {swot.regulatory_risk}/10",
                f"- **Overall Risk Score:** {swot.overall_risk_score}/10",
                "\n**Strengths:** " + ", ".join(swot.strengths),
                "**Weaknesses:** " + ", ".join(swot.weaknesses),
                "**Opportunities:** " + ", ".join(swot.opportunities),
                "**Threats:** " + ", ".join(swot.threats),
            ])
        else:
            lines.extend([
                "\n---",
                "## 3. SWOT Analysis and Risk Evaluation",
                "Evidence unavailable: SWOT and risk analysis could not be verified from available research."
            ])

        if mvp:
            lines.extend([
                "\n---",
                "## 4. Minimum Viable Product (MVP) Specifications",
                f"**Core Value Proposition:** {mvp.core_value_proposition}",
                f"**Recommended Technology Stack:** Frontend ({mvp.tech_stack_frontend}), Backend ({mvp.tech_stack_backend}), Database ({mvp.tech_stack_database}), AI Engine ({mvp.tech_stack_ai})",
                "\n### Core Feature Scope:"
            ])
            for feat in mvp.features:
                lines.append(f"- [{feat.priority}] **{feat.feature_name}** ({feat.estimated_days} days): {feat.description}")
        else:
            lines.extend([
                "\n---",
                "## 4. Minimum Viable Product (MVP) Specifications",
                "Evidence unavailable: MVP recommendations could not be established from available research."
            ])

        if gtm:
            lines.extend([
                "\n---",
                "## 5. Go-To-Market (GTM) Strategy",
                f"**Positioning Statement:** {gtm.positioning_statement}",
                f"**Pricing Architecture:** {gtm.pricing_strategy}",
                "\n**Customer Acquisition Channels:** " + ", ".join(gtm.primary_acquisition_channels),
            ])
        else:
            lines.extend([
                "\n---",
                "## 5. Go-To-Market (GTM) Strategy",
                "Evidence unavailable: GTM strategy could not be established from available research."
            ])

        if state.search_results:
            sources_lines = []
            categories = [
                ("Market Trends", getattr(state.search_results, "market_trends", [])),
                ("Competitors", getattr(state.search_results, "competitors", [])),
                ("Customer Pain Points", getattr(state.search_results, "customer_pain_points", [])),
                ("Industry News", getattr(state.search_results, "industry_news", [])),
                ("Funding & Deals", getattr(state.search_results, "funding", []))
            ]
            seen_u = set()
            for cat_name, cat_items in categories:
                for itm in cat_items:
                    u = getattr(itm, "url", "").strip()
                    if u and u not in seen_u:
                        seen_u.add(u)
                        q_str = f" [Query: {itm.query}]" if getattr(itm, "query", None) else ""
                        ts_str = f" (Retrieved: {itm.retrieved_at[:19]} UTC)" if getattr(itm, "retrieved_at", None) else ""
                        sources_lines.append(f"- **[{itm.title}]({u})** ({cat_name}){q_str}{ts_str}: {itm.snippet}")

            if sources_lines:
                lines.extend([
                    "\n---",
                    "## 6. Research Sources & Grounding Evidence"
                ])
                lines.extend(sources_lines)
            else:
                lines.extend([
                    "\n---",
                    "## 6. Research Sources & Grounding Evidence",
                    "Insufficient evidence / No live research available."
                ])
        else:
            lines.extend([
                "\n---",
                "## 6. Research Sources & Grounding Evidence",
                "Evidence unavailable: Live web research was unavailable or failed."
            ])

        content = "\n".join(lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return content

    @staticmethod
    def export_report_json(state: StartupState, output_path: str) -> None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))

    @staticmethod
    def export_report_pdf(state: StartupState, output_path: str) -> Optional[str]:
        """Generate an enterprise PDF validation report using ReportLab with clean typography,
        two-pass page numbering, robust data handling, and zero emojis."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            import urllib.parse
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, PageBreak, KeepTogether
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.pdfgen import canvas

            class NumberedCanvas(canvas.Canvas):
                """Two-pass canvas calculating total pages and rendering running headers/footers."""
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self._saved_page_states = []

                def showPage(self):
                    self._saved_page_states.append(dict(self.__dict__))
                    self._startPage()

                def save(self):
                    num_pages = len(self._saved_page_states)
                    for page_state in self._saved_page_states:
                        self.__dict__.update(page_state)
                        self.draw_decorations(num_pages)
                        canvas.Canvas.showPage(self)
                    canvas.Canvas.save(self)

                def draw_decorations(self, page_count: int):
                    self.saveState()
                    self.setFont("Helvetica", 8)
                    self.setFillColor(colors.HexColor("#64748B"))

                    # Running Header on pages > 1
                    if self._pageNumber > 1:
                        self.drawString(36, 756, "AI Startup Idea Validator  |  Executive Validation Report")
                        self.setStrokeColor(colors.HexColor("#CBD5E1"))
                        self.setLineWidth(0.5)
                        self.line(36, 750, 576, 750)

                    # Running Footer on all pages
                    self.setStrokeColor(colors.HexColor("#CBD5E1"))
                    self.setLineWidth(0.5)
                    self.line(36, 34, 576, 34)
                    self.drawString(36, 24, "CONFIDENTIAL  |  AI Startup Idea Validator")
                    page_str = f"Page {self._pageNumber} of {page_count}"
                    self.drawRightString(576, 24, page_str)
                    self.restoreState()

            # Helper functions for safe data formatting
            def _esc(val: Any, default: str = "Not available") -> str:
                if val is None:
                    return default
                s = str(val).strip()
                if not s or s.lower() == "none":
                    return default
                return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            def _fmt_url(url_val: Any, max_len: int = 48) -> str:
                if not url_val:
                    return "Not available"
                raw = str(url_val).strip()
                if not raw or raw.lower() == "none":
                    return "Not available"
                disp = raw if len(raw) <= max_len else raw[:max_len - 3] + "..."
                return f'<font color="#2563EB"><u>{_esc(disp)}</u></font>'

            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=36,
                leftMargin=36,
                topMargin=44,
                bottomMargin=44
            )

            styles = getSampleStyleSheet()
            normal = styles['Normal']

            # Typography styles
            app_meta_style = ParagraphStyle(
                'AppMeta',
                parent=normal,
                fontName='Helvetica-Bold',
                fontSize=9,
                leading=12,
                textColor=colors.HexColor('#2563EB'),
                spaceAfter=3
            )

            doc_title_style = ParagraphStyle(
                'DocTitleCustom',
                parent=normal,
                fontName='Helvetica-Bold',
                fontSize=18,
                leading=22,
                textColor=colors.HexColor('#0F172A'),
                spaceAfter=6
            )

            doc_subtitle_style = ParagraphStyle(
                'DocSubTitleCustom',
                parent=normal,
                fontName='Helvetica',
                fontSize=8.5,
                leading=12,
                textColor=colors.HexColor('#64748B'),
                spaceAfter=12
            )

            h1_style = ParagraphStyle(
                'H1_Custom',
                parent=normal,
                fontName='Helvetica-Bold',
                fontSize=12,
                leading=16,
                textColor=colors.HexColor('#0F172A'),
                spaceBefore=12,
                spaceAfter=6,
                keepWithNext=True
            )

            h2_style = ParagraphStyle(
                'H2_Custom',
                parent=normal,
                fontName='Helvetica-Bold',
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#1E293B'),
                spaceBefore=8,
                spaceAfter=4,
                keepWithNext=True
            )

            body_style = ParagraphStyle(
                'Body_Custom',
                parent=normal,
                fontName='Helvetica',
                fontSize=8.5,
                leading=12.5,
                textColor=colors.HexColor('#334155'),
                spaceAfter=4
            )

            body_bold = ParagraphStyle(
                'BodyBold_Custom',
                parent=normal,
                fontName='Helvetica-Bold',
                fontSize=8.5,
                leading=12.5,
                textColor=colors.HexColor('#1E293B'),
                spaceAfter=3
            )

            body_muted = ParagraphStyle(
                'BodyMuted_Custom',
                parent=normal,
                fontName='Helvetica-Oblique',
                fontSize=8,
                leading=11,
                textColor=colors.HexColor('#64748B'),
                spaceAfter=4
            )

            bullet_style = ParagraphStyle(
                'Bullet_Custom',
                parent=normal,
                fontName='Helvetica',
                fontSize=8.5,
                leading=12,
                textColor=colors.HexColor('#334155'),
                leftIndent=10,
                spaceAfter=3
            )

            th_style = ParagraphStyle(
                'TH_Custom',
                parent=normal,
                fontName='Helvetica-Bold',
                fontSize=8,
                leading=11,
                textColor=colors.HexColor('#FFFFFF')
            )

            td_style = ParagraphStyle(
                'TD_Custom',
                parent=normal,
                fontName='Helvetica',
                fontSize=8,
                leading=11.5,
                textColor=colors.HexColor('#334155')
            )

            td_bold = ParagraphStyle(
                'TDBold_Custom',
                parent=normal,
                fontName='Helvetica-Bold',
                fontSize=8,
                leading=11.5,
                textColor=colors.HexColor('#0F172A')
            )

            td_muted = ParagraphStyle(
                'TDMuted_Custom',
                parent=normal,
                fontName='Helvetica',
                fontSize=7.5,
                leading=10.5,
                textColor=colors.HexColor('#64748B')
            )

            story = []

            idea = state.idea
            report = state.final_report
            concept = state.structured_concept
            market = state.market_analysis
            comp = state.competitor_analysis
            swot = state.swot_analysis
            mvp = state.mvp_recommendation
            gtm = state.gtm_strategy
            search = state.search_results

            # Resolve Startup Name (kept distinct from idea text)
            startup_name = getattr(idea, "startup_name", None) or getattr(state, "startup_name", None)
            if not startup_name and concept and concept.unique_value_prop:
                uvp_words = concept.unique_value_prop.strip().split()
                if len(uvp_words) <= 6:
                    startup_name = concept.unique_value_prop.strip()
            if not startup_name:
                startup_name = "Active Venture Concept"

            val_timestamp = "Not available"
            if report and getattr(report, "timestamp", None):
                val_timestamp = str(report.timestamp).replace("T", " ")[:19] + " UTC"
            elif state.planning_output and getattr(state.planning_output, "timestamp", None):
                val_timestamp = str(state.planning_output.timestamp).replace("T", " ")[:19] + " UTC"

            # -------------------------------------------------------------
            # SECTION 1: COVER / EXECUTIVE SUMMARY
            # -------------------------------------------------------------
            story.append(Paragraph("AI STARTUP IDEA VALIDATOR", app_meta_style))
            story.append(Paragraph("Executive Startup Validation &amp; Strategic Decision Report", doc_title_style))
            story.append(Paragraph(
                f"<b>Startup Name:</b> {_esc(startup_name)} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Validation Date:</b> {_esc(val_timestamp)} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Report Classification:</b> Confidential Executive Brief",
                doc_subtitle_style
            ))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=10))
            story.append(Paragraph("1. Cover &amp; Executive Summary", h1_style))

            if report:
                verdict = report.verdict
                if verdict == "PROCEED":
                    verdict_bg = colors.HexColor("#DCFCE7")
                    verdict_fg = "#15803D"
                elif verdict in ["PIVOT", "CAUTION"]:
                    verdict_bg = colors.HexColor("#FEF3C7")
                    verdict_fg = "#B45309"
                else:
                    verdict_bg = colors.HexColor("#FEE2E2")
                    verdict_fg = "#B91C1C"

                score_val = getattr(report, "overall_viability_score", 0)

                # Investor-readiness line only if attributes exist and are meaningful
                investor_bits = []
                if getattr(report, "investor_readiness_score", None) is not None:
                    investor_bits.append(f"Investor Readiness: <b>{report.investor_readiness_score}/100</b>")
                if getattr(report, "funding_probability", None) is not None:
                    investor_bits.append(f"Funding Probability: <b>{report.funding_probability}%</b>")
                if getattr(report, "pmf_score", None) is not None:
                    investor_bits.append(f"PMF Score: <b>{report.pmf_score}/100</b>")
                if getattr(report, "confidence_score", None) is not None:
                    investor_bits.append(f"Confidence Index: <b>{report.confidence_score}%</b>")

                investor_line = " &nbsp;|&nbsp; ".join(investor_bits) if investor_bits else "Investor Metrics: Not available"

                score_card_data = [
                    [
                        Paragraph(f"<font size=20 color='{verdict_fg}'><b>{score_val}/100</b></font><br/><font size=8 color='#64748B'>Deterministic Viability Score</font>", body_style),
                        Paragraph(f"<font size=14 color='{verdict_fg}'><b>STRATEGIC VERDICT: {_esc(verdict)}</b></font><br/><font size=8 color='#475569'>{investor_line}</font>", body_style)
                    ]
                ]
                score_card_table = Table(score_card_data, colWidths=[150, 390])
                score_card_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
                    ('BACKGROUND', (1, 0), (1, -1), verdict_bg),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('PADDING', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(score_card_table)
                story.append(Spacer(1, 8))

                story.append(Paragraph("Executive Summary", h2_style))
                exec_text = getattr(report, "executive_summary", "")
                story.append(Paragraph(_esc(exec_text) if exec_text else "Not available", body_style))
                story.append(Spacer(1, 6))

            # -------------------------------------------------------------
            # SECTION 2: STARTUP IDEA & BUSINESS PROFILE
            # -------------------------------------------------------------
            story.append(Paragraph("2. Startup Idea &amp; Business Profile", h1_style))

            idea_box_data = [
                [Paragraph(f"<b>Startup Name:</b> {_esc(startup_name)}", body_bold)],
                [Paragraph(f"<b>Original Concept Description:</b><br/>{_esc(idea.idea_text)}", body_style)]
            ]
            idea_box_table = Table(idea_box_data, colWidths=[540])
            idea_box_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('PADDING', (0, 0), (-1, -1), 7),
            ]))
            story.append(idea_box_table)
            story.append(Spacer(1, 6))

            profile_data = [
                [
                    Paragraph("<b>Target Industry:</b>", td_bold),
                    Paragraph(_esc(idea.target_industry), td_style),
                    Paragraph("<b>Target Audience:</b>", td_bold),
                    Paragraph(_esc(idea.target_audience), td_style)
                ],
                [
                    Paragraph("<b>Business Model:</b>", td_bold),
                    Paragraph(_esc(idea.business_model), td_style),
                    Paragraph("<b>Estimated Budget:</b>", td_bold),
                    Paragraph(_esc(idea.budget), td_style)
                ],
                [
                    Paragraph("<b>Launch Timeline:</b>", td_bold),
                    Paragraph(_esc(idea.timeline), td_style),
                    Paragraph("<b>Validation Status:</b>", td_bold),
                    Paragraph(_esc(state.status).title(), td_style)
                ]
            ]
            profile_table = Table(profile_data, colWidths=[110, 160, 110, 160])
            profile_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFFFF')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(profile_table)

            if concept:
                story.append(Spacer(1, 6))
                concept_data = []
                if concept.problem:
                    concept_data.append([Paragraph("<b>Problem:</b>", td_bold), Paragraph(_esc(concept.problem), td_style)])
                if concept.solution:
                    concept_data.append([Paragraph("<b>Solution:</b>", td_bold), Paragraph(_esc(concept.solution), td_style)])
                if concept.unique_value_prop:
                    concept_data.append([Paragraph("<b>Core UVP:</b>", td_bold), Paragraph(_esc(concept.unique_value_prop), td_style)])
                if concept_data:
                    c_table = Table(concept_data, colWidths=[90, 450])
                    c_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                        ('PADDING', (0, 0), (-1, -1), 4),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(c_table)

            story.append(PageBreak())

            # -------------------------------------------------------------
            # SECTION 3: SCORECARD
            # -------------------------------------------------------------
            story.append(Paragraph("3. Deterministic Viability Scorecard", h1_style))
            story.append(Paragraph(
                "Deterministic multi-factor viability assessment derived from the 8-dimension mathematical scoring engine:",
                body_style
            ))

            scoring = getattr(report, "scoring_breakdown", None) if report else None

            # All 8 real dimensions with max points from services.scoring_engine
            dimensions_config = [
                ("Market Opportunity", getattr(scoring, "market_opportunity_score", None), 20),
                ("Innovation & Differentiation", getattr(scoring, "innovation_score", None), 15),
                ("Competition & Defensible Moat", getattr(scoring, "competition_score", None), 15),
                ("Scalability Potential", getattr(scoring, "scalability_score", None), 15),
                ("Technical Feasibility", getattr(scoring, "technical_feasibility_score", None), 10),
                ("Revenue Model Viability", getattr(scoring, "revenue_model_score", None), 10),
                ("Execution & Risk Resilience", getattr(scoring, "execution_risk_score", None), 10),
                ("Market Timing", getattr(scoring, "market_timing_score", None), 5),
            ]

            scorecard_rows = [
                [
                    Paragraph("<b>Evaluation Dimension</b>", th_style),
                    Paragraph("<b>Score</b>", th_style),
                    Paragraph("<b>Max Points</b>", th_style),
                    Paragraph("<b>Performance</b>", th_style)
                ]
            ]

            for dim_name, actual_score, max_pts in dimensions_config:
                if actual_score is not None:
                    pct = (actual_score / max_pts * 100.0)
                    pct_str = f"{pct:.1f}%"
                    score_str = f"{actual_score}"
                else:
                    score_str = "Not available"
                    pct_str = "Not available"

                scorecard_rows.append([
                    Paragraph(dim_name, td_bold),
                    Paragraph(score_str, td_style),
                    Paragraph(str(max_pts), td_style),
                    Paragraph(pct_str, td_style)
                ])

            # Total row
            tot_score = getattr(scoring, "total_viability_score", getattr(report, "overall_viability_score", "N/A")) if (scoring or report) else "N/A"
            rep_verdict = getattr(scoring, "verdict", getattr(report, "verdict", "N/A")) if (scoring or report) else "N/A"
            scorecard_rows.append([
                Paragraph("<b>Total Viability Score</b>", td_bold),
                Paragraph(f"<b>{tot_score}</b>", td_bold),
                Paragraph("<b>100</b>", td_bold),
                Paragraph(f"<b>Verdict: {_esc(rep_verdict)}</b>", td_bold)
            ])

            scorecard_table = Table(scorecard_rows, colWidths=[230, 95, 95, 120], repeatRows=1)
            scorecard_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(scorecard_table)
            story.append(Spacer(1, 6))

            if scoring and getattr(scoring, "reasoning_why", None):
                story.append(Paragraph("Factor Attribution &amp; Explainable Reasoning (WHY):", h2_style))
                for r_item in scoring.reasoning_why:
                    story.append(Paragraph(f"&bull; {_esc(r_item)}", bullet_style))
                story.append(Spacer(1, 6))

            # -------------------------------------------------------------
            # SECTION 4: MARKET OPPORTUNITY
            # -------------------------------------------------------------
            story.append(Paragraph("4. Market Opportunity &amp; Sizing Metrics", h1_style))
            if market:
                tam_str = f"${market.tam_billions}B" if getattr(market, "tam_billions", None) is not None else "Evidence unavailable"
                sam_str = f"${market.sam_billions}B" if getattr(market, "sam_billions", None) is not None else "Evidence unavailable"
                som_str = f"${market.som_billions}B" if getattr(market, "som_billions", None) is not None else "Evidence unavailable"
                cagr_str = f"{market.cagr_percentage}%" if getattr(market, "cagr_percentage", None) is not None else "Evidence unavailable"
                readiness_str = f"{market.market_readiness_score}/100" if getattr(market, "market_readiness_score", None) is not None else "Evidence unavailable"

                m_metrics_data = [
                    [
                        Paragraph("<b>Total Addressable Market (TAM)</b>", td_bold),
                        Paragraph("<b>Serviceable Addressable Market (SAM)</b>", td_bold),
                        Paragraph("<b>Serviceable Obtainable Market (SOM)</b>", td_bold),
                        Paragraph("<b>Projected CAGR</b>", td_bold)
                    ],
                    [
                        Paragraph(f"<font size=11 color='#1E293B'><b>{tam_str}</b></font>", td_style),
                        Paragraph(f"<font size=11 color='#1E293B'><b>{sam_str}</b></font>", td_style),
                        Paragraph(f"<font size=11 color='#1E293B'><b>{som_str}</b></font>", td_style),
                        Paragraph(f"<font size=11 color='#15803D'><b>{cagr_str}</b></font>", td_style)
                    ]
                ]
                m_metrics_table = Table(m_metrics_data, colWidths=[135, 135, 135, 135])
                m_metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(m_metrics_table)
                story.append(Spacer(1, 6))

                if getattr(market, "market_size_summary", None):
                    story.append(Paragraph(f"<b>Market Dynamics:</b> {_esc(market.market_size_summary)} (Readiness Score: {readiness_str})", body_style))

                if getattr(market, "key_growth_drivers", None):
                    story.append(Paragraph("Primary Growth Drivers:", h2_style))
                    for drv in market.key_growth_drivers:
                        story.append(Paragraph(f"&bull; {_esc(drv)}", bullet_style))

                if getattr(market, "target_personas", None):
                    story.append(Paragraph("Target Customer Personas &amp; Demand Indicators:", h2_style))
                    persona_rows = [
                        [
                            Paragraph("<b>Customer Segment / Role</b>", th_style),
                            Paragraph("<b>Identified Pain Points &amp; Friction</b>", th_style),
                            Paragraph("<b>Willingness to Pay</b>", th_style)
                        ]
                    ]
                    for p in market.target_personas:
                        p_role = getattr(p, "role", "Target User")
                        p_pains = "<br/>".join([f"- {_esc(x)}" for x in getattr(p, "pain_points", [])]) if getattr(p, "pain_points", None) else "Not specified"
                        p_wtp = getattr(p, "willingness_to_pay", "Medium")
                        persona_rows.append([
                            Paragraph(_esc(p_role), td_bold),
                            Paragraph(p_pains, td_style),
                            Paragraph(_esc(p_wtp), td_style)
                        ])
                    p_table = Table(persona_rows, colWidths=[150, 260, 130], repeatRows=1)
                    p_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                        ('PADDING', (0, 0), (-1, -1), 5),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(p_table)
            else:
                story.append(Paragraph("Market size could not be established from available research.", body_muted))

            story.append(PageBreak())

            # -------------------------------------------------------------
            # SECTION 5: COMPETITOR INTELLIGENCE
            # -------------------------------------------------------------
            story.append(Paragraph("5. Competitor Intelligence &amp; Defensible Positioning", h1_style))
            if comp:
                if getattr(comp, "market_positioning_summary", None):
                    story.append(Paragraph(f"<b>Market Positioning:</b> {_esc(comp.market_positioning_summary)}", body_style))
                if getattr(comp, "moat_assessment", None):
                    story.append(Paragraph(f"<b>Competitive Moat:</b> {_esc(comp.moat_assessment)}", body_style))
                story.append(Spacer(1, 6))

                competitors_list = []
                for c in getattr(comp, "direct_competitors", []):
                    competitors_list.append((c, "Direct Competitor"))
                for c in getattr(comp, "indirect_competitors", []):
                    competitors_list.append((c, "Indirect / Status Quo"))

                if competitors_list:
                    comp_rows = [
                        [
                            Paragraph("<b>Competitor &amp; Type</b>", th_style),
                            Paragraph("<b>Description &amp; Pricing</b>", th_style),
                            Paragraph("<b>Strengths</b>", th_style),
                            Paragraph("<b>Weaknesses</b>", th_style)
                        ]
                    ]
                    for c_obj, c_type in competitors_list:
                        c_name = getattr(c_obj, "name", "Competitor")
                        c_desc = getattr(c_obj, "description", "Not available")
                        c_pricing = (getattr(c_obj, "pricing_model", None) or "").strip() or "Not available"
                        c_str_list = getattr(c_obj, "strengths", [])
                        c_wk_list = getattr(c_obj, "weaknesses", [])

                        c_str = "<br/>".join([f"+ {_esc(s)}" for s in c_str_list]) if c_str_list else "None listed"
                        c_wk = "<br/>".join([f"- {_esc(w)}" for w in c_wk_list]) if c_wk_list else "None listed"

                        comp_rows.append([
                            Paragraph(f"<b>{_esc(c_name)}</b><br/><font color='#64748B' size=7>{_esc(c_type)}</font>", td_style),
                            Paragraph(f"{_esc(c_desc)}<br/><font color='#475569'><i>Pricing: {_esc(c_pricing)}</i></font>", td_style),
                            Paragraph(c_str, td_style),
                            Paragraph(c_wk, td_style)
                        ])

                    comp_table = Table(comp_rows, colWidths=[125, 145, 135, 135], repeatRows=1)
                    comp_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                        ('PADDING', (0, 0), (-1, -1), 5),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(comp_table)
                else:
                    story.append(Paragraph("No verified competitors identified from available research.", body_muted))
            else:
                story.append(Paragraph("No verified competitors identified from available research.", body_muted))

            story.append(Spacer(1, 10))

            # -------------------------------------------------------------
            # SECTION 6: SWOT & RISK
            # -------------------------------------------------------------
            story.append(Paragraph("6. SWOT Analysis &amp; Enterprise Risk Evaluation", h1_style))
            if swot:
                # 4-Quadrant SWOT Table
                swot_s = "<br/>".join([f"&bull; {_esc(x)}" for x in getattr(swot, "strengths", [])]) or "Not available"
                swot_w = "<br/>".join([f"&bull; {_esc(x)}" for x in getattr(swot, "weaknesses", [])]) or "Not available"
                swot_o = "<br/>".join([f"&bull; {_esc(x)}" for x in getattr(swot, "opportunities", [])]) or "Not available"
                swot_t = "<br/>".join([f"&bull; {_esc(x)}" for x in getattr(swot, "threats", [])]) or "Not available"

                swot_grid = [
                    [
                        Paragraph("<b>STRENGTHS (Internal)</b>", th_style),
                        Paragraph("<b>WEAKNESSES (Internal)</b>", th_style)
                    ],
                    [
                        Paragraph(swot_s, td_style),
                        Paragraph(swot_w, td_style)
                    ],
                    [
                        Paragraph("<b>OPPORTUNITIES (External)</b>", th_style),
                        Paragraph("<b>THREATS (External)</b>", th_style)
                    ],
                    [
                        Paragraph(swot_o, td_style),
                        Paragraph(swot_t, td_style)
                    ]
                ]
                swot_table = Table(swot_grid, colWidths=[270, 270])
                swot_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#1E293B')),
                    ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#334155')),
                    ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#1E293B')),
                    ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#334155')),
                    ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8FAFC')),
                    ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#FFFFFF')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(swot_table)
                story.append(Spacer(1, 8))

                # Risk Indices
                f_risk = getattr(swot, "financial_risk", "N/A")
                t_risk = getattr(swot, "technical_risk", "N/A")
                r_risk = getattr(swot, "regulatory_risk", "N/A")
                o_risk = getattr(swot, "overall_risk_score", "N/A")

                risk_idx_data = [
                    [
                        Paragraph("<b>Financial Risk:</b>", td_bold),
                        Paragraph(f"{f_risk}/10", td_style),
                        Paragraph("<b>Technical Risk:</b>", td_bold),
                        Paragraph(f"{t_risk}/10", td_style),
                        Paragraph("<b>Regulatory Risk:</b>", td_bold),
                        Paragraph(f"{r_risk}/10", td_style),
                        Paragraph("<b>Overall Risk:</b>", td_bold),
                        Paragraph(f"<b>{o_risk}/10</b>", td_bold)
                    ]
                ]
                risk_idx_table = Table(risk_idx_data, colWidths=[70, 65, 70, 65, 70, 65, 70, 65])
                risk_idx_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0, 0), (-1, -1), 4),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(risk_idx_table)
                story.append(Spacer(1, 6))

                # Risk Matrix Table
                if getattr(swot, "risk_matrix", None):
                    story.append(Paragraph("Enterprise Risk Matrix &amp; Mitigation Strategies:", h2_style))
                    risk_rows = [
                        [
                            Paragraph("<b>Risk Description</b>", th_style),
                            Paragraph("<b>Category</b>", th_style),
                            Paragraph("<b>Prob</b>", th_style),
                            Paragraph("<b>Impact</b>", th_style),
                            Paragraph("<b>Severity</b>", th_style),
                            Paragraph("<b>Mitigation Strategy</b>", th_style)
                        ]
                    ]
                    for rk in swot.risk_matrix:
                        r_name = getattr(rk, "risk_name", getattr(rk, "name", "Identified Risk"))
                        r_cat = getattr(rk, "category", "General")
                        r_prob = getattr(rk, "probability", 3)
                        r_imp = getattr(rk, "impact", 3)
                        r_sev = getattr(rk, "severity_score", getattr(rk, "severity", r_prob * r_imp))
                        r_mit = getattr(rk, "mitigation_strategy", getattr(rk, "mitigation", "Standard operational controls."))

                        risk_rows.append([
                            Paragraph(_esc(r_name), td_bold),
                            Paragraph(_esc(r_cat), td_style),
                            Paragraph(f"{r_prob}/5", td_style),
                            Paragraph(f"{r_imp}/5", td_style),
                            Paragraph(f"<b>{r_sev}</b>/25", td_style),
                            Paragraph(_esc(r_mit), td_style)
                        ])

                    risk_table = Table(risk_rows, colWidths=[120, 65, 45, 45, 55, 210], repeatRows=1)
                    risk_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                        ('PADDING', (0, 0), (-1, -1), 4),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(risk_table)

                if getattr(swot, "risk_mitigation_plan", None):
                    story.append(Spacer(1, 4))
                    story.append(Paragraph("Strategic Risk Mitigation Directives:", h2_style))
                    for m_item in swot.risk_mitigation_plan:
                        story.append(Paragraph(f"&bull; {_esc(m_item)}", bullet_style))
            else:
                story.append(Paragraph("SWOT and risk analysis data not available.", body_muted))

            story.append(PageBreak())

            # -------------------------------------------------------------
            # SECTION 7: MVP BLUEPRINT
            # -------------------------------------------------------------
            story.append(Paragraph("7. Minimum Viable Product (MVP) Blueprint", h1_style))
            if mvp:
                if getattr(mvp, "core_value_proposition", None):
                    story.append(Paragraph(f"<b>Core MVP Value Proposition:</b> {_esc(mvp.core_value_proposition)}", body_style))
                    story.append(Spacer(1, 4))

                # Tech Stack Table
                tech_data = [
                    [
                        Paragraph("<b>Frontend</b>", td_bold),
                        Paragraph("<b>Backend Architecture</b>", td_bold),
                        Paragraph("<b>Database Layer</b>", td_bold),
                        Paragraph("<b>AI / LLM Engine</b>", td_bold)
                    ],
                    [
                        Paragraph(_esc(getattr(mvp, "tech_stack_frontend", "Not available")), td_style),
                        Paragraph(_esc(getattr(mvp, "tech_stack_backend", "Not available")), td_style),
                        Paragraph(_esc(getattr(mvp, "tech_stack_database", "Not available")), td_style),
                        Paragraph(_esc(getattr(mvp, "tech_stack_ai", "Not available")), td_style)
                    ]
                ]
                tech_table = Table(tech_data, colWidths=[135, 135, 135, 135])
                tech_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0, 0), (-1, -1), 4),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(tech_table)
                story.append(Spacer(1, 6))

                # Features Scope
                if getattr(mvp, "features", None):
                    story.append(Paragraph("Prioritized Feature Scope:", h2_style))
                    feat_rows = [
                        [
                            Paragraph("<b>Feature Name</b>", th_style),
                            Paragraph("<b>Priority</b>", th_style),
                            Paragraph("<b>Est. Days</b>", th_style),
                            Paragraph("<b>Functional Specification</b>", th_style)
                        ]
                    ]
                    for f in mvp.features:
                        feat_rows.append([
                            Paragraph(_esc(getattr(f, "feature_name", "Feature")), td_bold),
                            Paragraph(_esc(getattr(f, "priority", "Must Have")), td_style),
                            Paragraph(f"{getattr(f, 'estimated_days', 5)} days", td_style),
                            Paragraph(_esc(getattr(f, "description", "")), td_style)
                        ])
                    feat_table = Table(feat_rows, colWidths=[130, 80, 60, 270], repeatRows=1)
                    feat_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                        ('PADDING', (0, 0), (-1, -1), 4),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(feat_table)
                    story.append(Spacer(1, 6))

                # Roadmap
                if getattr(mvp, "four_week_roadmap", None):
                    story.append(Paragraph("4-Week Execution Roadmap:", h2_style))
                    roadmap_rows = [
                        [
                            Paragraph("<b>Phase / Week</b>", th_style),
                            Paragraph("<b>Milestones &amp; Deliverables</b>", th_style)
                        ]
                    ]
                    for wk, milestone in mvp.four_week_roadmap.items():
                        roadmap_rows.append([
                            Paragraph(_esc(wk), td_bold),
                            Paragraph(_esc(milestone), td_style)
                        ])
                    rm_table = Table(roadmap_rows, colWidths=[90, 450], repeatRows=1)
                    rm_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                        ('PADDING', (0, 0), (-1, -1), 4),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(rm_table)

                # Validation KPIs
                if getattr(mvp, "key_metrics_kpis", None):
                    story.append(Spacer(1, 4))
                    story.append(Paragraph("Validation KPIs &amp; Success Criteria:", h2_style))
                    for kpi in mvp.key_metrics_kpis:
                        story.append(Paragraph(f"&bull; {_esc(kpi)}", bullet_style))
            else:
                story.append(Paragraph("MVP blueprint data not available.", body_muted))

            story.append(Spacer(1, 10))

            # -------------------------------------------------------------
            # SECTION 8: GTM STRATEGY
            # -------------------------------------------------------------
            story.append(Paragraph("8. Go-To-Market (GTM) Strategy", h1_style))
            if gtm:
                if getattr(gtm, "positioning_statement", None):
                    story.append(Paragraph(f"<b>Strategic Positioning:</b> {_esc(gtm.positioning_statement)}", body_style))
                if getattr(gtm, "pricing_strategy", None):
                    story.append(Paragraph(f"<b>Pricing Architecture:</b> {_esc(gtm.pricing_strategy)}", body_style))
                if getattr(gtm, "estimated_cac_summary", None):
                    story.append(Paragraph(f"<b>Unit Economics &amp; Estimated CAC:</b> {_esc(gtm.estimated_cac_summary)}", body_style))
                story.append(Spacer(1, 4))

                if getattr(gtm, "primary_acquisition_channels", None):
                    story.append(Paragraph("Primary Customer Acquisition Channels:", h2_style))
                    for ch in gtm.primary_acquisition_channels:
                        story.append(Paragraph(f"&bull; {_esc(ch)}", bullet_style))

                if getattr(gtm, "launch_tactics", None):
                    story.append(Paragraph("Tactical Launch Roadmap:", h2_style))
                    for tc in gtm.launch_tactics:
                        story.append(Paragraph(f"&bull; {_esc(tc)}", bullet_style))
            else:
                story.append(Paragraph("GTM strategy data not available.", body_muted))

            story.append(PageBreak())

            # -------------------------------------------------------------
            # SECTION 9: FINAL VALIDATION
            # -------------------------------------------------------------
            story.append(Paragraph("9. Final Validation Assessment &amp; Strategic Roadmap", h1_style))
            if report:
                story.append(Paragraph(
                    f"<b>Strategic Verdict:</b> <font color='{verdict_fg}'><b>{_esc(report.verdict)}</b></font> &nbsp;|&nbsp; "
                    f"<b>Overall Viability Index:</b> {report.overall_viability_score}/100",
                    body_bold
                ))
                story.append(Spacer(1, 4))

                if getattr(report, "key_takeaways", None):
                    story.append(Paragraph("Critical Success Factors &amp; Key Findings:", h2_style))
                    for tk in report.key_takeaways:
                        story.append(Paragraph(f"&bull; {_esc(tk)}", bullet_style))
                    story.append(Spacer(1, 4))

                if getattr(report, "recommended_next_steps", None):
                    story.append(Paragraph("Recommended Prioritized Action Plan:", h2_style))
                    for idx, step in enumerate(report.recommended_next_steps, 1):
                        story.append(Paragraph(f"<b>{idx}.</b> {_esc(step)}", bullet_style))
            else:
                story.append(Paragraph("Final report assessment not available.", body_muted))

            story.append(Spacer(1, 10))

            # -------------------------------------------------------------
            # SECTION 10: RESEARCH SOURCES
            # -------------------------------------------------------------
            story.append(Paragraph("10. Research Sources &amp; Grounding Evidence", h1_style))
            story.append(Paragraph(
                "Real research sources extracted from automated multi-agent market discovery:",
                body_muted
            ))

            collected_sources = []
            seen_urls = set()

            if search:
                categories = [
                    ("Market Trends", getattr(search, "market_trends", [])),
                    ("Competitors", getattr(search, "competitors", [])),
                    ("Customer Pain Points", getattr(search, "customer_pain_points", [])),
                    ("Industry News", getattr(search, "industry_news", [])),
                    ("Funding & Deals", getattr(search, "funding", []))
                ]
                for cat_label, item_list in categories:
                    if item_list:
                        for item in item_list:
                            u = getattr(item, "url", "").strip()
                            if u and u not in seen_urls:
                                seen_urls.add(u)
                                collected_sources.append((item, cat_label))

            if collected_sources:
                sources_rows = [
                    [
                        Paragraph("<b>#</b>", th_style),
                        Paragraph("<b>Source Title &amp; Domain</b>", th_style),
                        Paragraph("<b>Reference URL</b>", th_style),
                        Paragraph("<b>Evidence Snippet</b>", th_style)
                    ]
                ]
                for s_idx, (s_item, s_cat) in enumerate(collected_sources, 1):
                    s_title = getattr(s_item, "title", "Reference Link")
                    s_url = getattr(s_item, "url", "")
                    s_snip = getattr(s_item, "snippet", "")
                    domain = "Web Source"
                    if s_url:
                        try:
                            domain = urllib.parse.urlparse(s_url).netloc or "Web Source"
                        except Exception:
                            domain = "Web Source"

                    snippet_clean = _esc(s_snip[:180] + "..." if len(s_snip) > 180 else s_snip) if s_snip else "Snippet not captured."

                    sources_rows.append([
                        Paragraph(str(s_idx), td_bold),
                        Paragraph(f"<b>{_esc(s_title)}</b><br/><font color='#64748B' size=7>{_esc(domain)} ({_esc(s_cat)})</font>", td_style),
                        Paragraph(_fmt_url(s_url, max_len=36), td_style),
                        Paragraph(snippet_clean, td_muted)
                    ])

                sources_table = Table(sources_rows, colWidths=[25, 175, 160, 180], repeatRows=1)
                sources_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0, 0), (-1, -1), 4),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(sources_table)
            else:
                story.append(Paragraph("No automated web discovery sources recorded for this validation session.", body_muted))

            doc.build(story, canvasmaker=NumberedCanvas)
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}", exc_info=True)
            return None
