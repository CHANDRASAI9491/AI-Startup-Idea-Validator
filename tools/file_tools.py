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
            lines.extend([
                "\n---",
                "## 1. Market Sizing and Growth Analysis",
                f"- **Total Addressable Market (TAM):** ${market.tam_billions}B",
                f"- **Serviceable Addressable Market (SAM):** ${market.sam_billions}B",
                f"- **Serviceable Obtainable Market (SOM):** ${market.som_billions}B",
                f"- **Projected CAGR:** {market.cagr_percentage}%",
                f"- **Market Readiness Score:** {market.market_readiness_score}/100",
                f"\n**Market Scope Summary:** {market.market_size_summary}",
                "\n**Primary Growth Drivers:**"
            ])
            for driver in market.key_growth_drivers:
                lines.append(f"- {driver}")

        if comp:
            lines.extend([
                "\n---",
                "## 2. Competitive Intelligence and Moat",
                f"**Market Positioning:** {comp.market_positioning_summary}",
                f"**Competitive Moat:** {comp.moat_assessment}",
                "\n### Direct Competitors:"
            ])
            for c in comp.direct_competitors:
                lines.append(f"- **{c.name}** ({c.pricing_model}): {c.description}")

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

        if gtm:
            lines.extend([
                "\n---",
                "## 5. Go-To-Market (GTM) Strategy",
                f"**Positioning Statement:** {gtm.positioning_statement}",
                f"**Pricing Architecture:** {gtm.pricing_strategy}",
                "\n**Customer Acquisition Channels:** " + ", ".join(gtm.primary_acquisition_channels),
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
        """Generate an enterprise PDF validation report using ReportLab with clean typography and zero emojis."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
            )

            styles = getSampleStyleSheet()
            normal = styles['Normal']
            
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor('#0F172A'),
                spaceAfter=8
            )

            subtitle_style = ParagraphStyle(
                'DocSubTitle',
                parent=normal,
                fontSize=10,
                textColor=colors.HexColor('#475569'),
                spaceAfter=14
            )

            h2_style = ParagraphStyle(
                'Heading2_Custom',
                parent=styles['Heading2'],
                fontSize=13,
                leading=17,
                textColor=colors.HexColor('#1E293B'),
                spaceBefore=14,
                spaceAfter=6
            )

            body_style = ParagraphStyle(
                'Body_Custom',
                parent=normal,
                fontSize=9.5,
                leading=13.5,
                textColor=colors.HexColor('#334155'),
                spaceAfter=5
            )

            story = []

            idea = state.idea
            report = state.final_report

            # Document Title
            story.append(Paragraph("Enterprise AI Startup Validation & Decision Report", title_style))
            story.append(Paragraph(f"<b>Concept Description:</b> {idea.idea_text}<br/><b>Industry Sector:</b> {idea.target_industry} | <b>Target Audience:</b> {idea.target_audience} | <b>Business Model:</b> {idea.business_model}", subtitle_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=14))

            if report:
                # Score & Verdict Box
                verdict_color = "#15803D" if report.verdict == "PROCEED" else ("#B45309" if report.verdict in ["PIVOT", "CAUTION"] else "#B91C1C")
                
                score_table_data = [
                    [
                        Paragraph(f"<font size=15 color='{verdict_color}'><b>{report.overall_viability_score}/100</b></font><br/><font size=8 color='#64748B'>Viability Score</font>", body_style),
                        Paragraph(f"<font size=13 color='{verdict_color}'><b>VERDICT: {report.verdict}</b></font><br/><font size=8 color='#64748B'>Investor Readiness: {report.investor_readiness_score}/100 | Funding Prob: {report.funding_probability}%</font>", body_style)
                    ]
                ]
                t = Table(score_table_data, colWidths=[160, 340])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0,0), (-1,-1), 10),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                story.append(t)
                story.append(Spacer(1, 14))

                story.append(Paragraph("Executive Summary", h2_style))
                story.append(Paragraph(report.executive_summary, body_style))
                story.append(Spacer(1, 8))

            # Market Analysis
            if state.market_analysis:
                m = state.market_analysis
                story.append(Paragraph("1. Market Sizing and Growth Metrics", h2_style))
                story.append(Paragraph(f"<b>TAM:</b> ${m.tam_billions}B | <b>SAM:</b> ${m.sam_billions}B | <b>SOM:</b> ${m.som_billions}B | <b>Projected CAGR:</b> {m.cagr_percentage}%", body_style))
                story.append(Paragraph(m.market_size_summary, body_style))
                story.append(Spacer(1, 8))

            # Competitor Analysis
            if state.competitor_analysis:
                c = state.competitor_analysis
                story.append(Paragraph("2. Competitive Intelligence and Positioning", h2_style))
                story.append(Paragraph(f"<b>Market Positioning:</b> {c.market_positioning_summary}", body_style))
                story.append(Paragraph(f"<b>Competitive Moat:</b> {c.moat_assessment}", body_style))
                story.append(Spacer(1, 8))

            # SWOT
            if state.swot_analysis:
                s = state.swot_analysis
                story.append(Paragraph("3. SWOT Analysis and Risk Evaluation", h2_style))
                story.append(Paragraph(f"<b>Strengths:</b> {', '.join(s.strengths)}", body_style))
                story.append(Paragraph(f"<b>Weaknesses:</b> {', '.join(s.weaknesses)}", body_style))
                story.append(Paragraph(f"<b>Opportunities:</b> {', '.join(s.opportunities)}", body_style))
                story.append(Paragraph(f"<b>Threats:</b> {', '.join(s.threats)}", body_style))
                story.append(Spacer(1, 8))

            doc.build(story)
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            return None
