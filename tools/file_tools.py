import os
import json
import logging
from typing import Dict, Any, Optional
from state.schema import StartupState, AgentState

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

        lines = [
            f"# Startup Idea Validation Report: {idea.idea_text}",
            f"**Generated at:** {report.timestamp if report else 'N/A'}",
            f"**Industry:** {idea.target_industry} | **Target Audience:** {idea.target_audience}",
            "\n---",
            "## Executive Summary",
            f"**Overall Viability Score:** {report.overall_viability_score}/100" if report else "",
            f"**Verdict:** `{report.verdict}`" if report else "",
            f"\n{report.executive_summary if report else ''}",
            "\n### Key Takeaways",
        ]

        if report:
            for t in report.key_takeaways:
                lines.append(f"- {t}")

            lines.append("\n### Recommended Next Steps")
            for step in report.recommended_next_steps:
                lines.append(f"1. {step}")

        if market:
            lines.extend([
                "\n---",
                "## 1. Market Analysis",
                f"- **TAM (Total Addressable Market):** ${market.tam_billions}B",
                f"- **SAM (Serviceable Addressable Market):** ${market.sam_billions}B",
                f"- **SOM (Serviceable Obtainable Market):** ${market.som_billions}B",
                f"- **CAGR:** {market.cagr_percentage}%",
                f"- **Market Readiness Score:** {market.market_readiness_score}/100",
                f"\n**Summary:** {market.market_size_summary}",
                "\n**Key Growth Drivers:**"
            ])
            for driver in market.key_growth_drivers:
                lines.append(f"- {driver}")

        if comp:
            lines.extend([
                "\n---",
                "## 2. Competitor Analysis",
                f"**Market Positioning:** {comp.market_positioning_summary}",
                f"**Moat Assessment:** {comp.moat_assessment}",
                "\n### Direct Competitors:"
            ])
            for c in comp.direct_competitors:
                lines.append(f"- **{c.name}** ({c.pricing_model}): {c.description}")

        if swot:
            lines.extend([
                "\n---",
                "## 3. SWOT & Risk Assessment",
                f"- **Financial Risk:** {swot.financial_risk}/10",
                f"- **Technical Risk:** {swot.technical_risk}/10",
                f"- **Regulatory Risk:** {swot.regulatory_risk}/10",
                f"- **Overall Risk Level:** {swot.overall_risk_score}/10",
                "\n**Strengths:** " + ", ".join(swot.strengths),
                "**Weaknesses:** " + ", ".join(swot.weaknesses),
                "**Opportunities:** " + ", ".join(swot.opportunities),
                "**Threats:** " + ", ".join(swot.threats),
            ])

        if mvp:
            lines.extend([
                "\n---",
                "## 4. MVP Recommendation",
                f"**Core Value Proposition:** {mvp.core_value_proposition}",
                f"**Recommended Tech Stack:** Frontend ({mvp.tech_stack_frontend}), Backend ({mvp.tech_stack_backend}), DB ({mvp.tech_stack_database}), AI ({mvp.tech_stack_ai})",
                "\n### Key Features Scope:"
            ])
            for feat in mvp.features:
                lines.append(f"- [{feat.priority}] **{feat.feature_name}** ({feat.estimated_days} days): {feat.description}")

        if gtm:
            lines.extend([
                "\n---",
                "## 5. Go-To-Market Strategy",
                f"**Positioning Statement:** {gtm.positioning_statement}",
                f"**Pricing Strategy:** {gtm.pricing_strategy}",
                "\n**Primary Channels:** " + ", ".join(gtm.primary_acquisition_channels),
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
        """Generate a clean, styled PDF validation report using ReportLab."""
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
                textColor=colors.HexColor('#1E293B'),
                spaceAfter=10
            )

            subtitle_style = ParagraphStyle(
                'DocSubTitle',
                parent=normal,
                fontSize=10,
                textColor=colors.HexColor('#64748B'),
                spaceAfter=15
            )

            h2_style = ParagraphStyle(
                'Heading2_Custom',
                parent=styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor('#0F172A'),
                spaceBefore=15,
                spaceAfter=8
            )

            body_style = ParagraphStyle(
                'Body_Custom',
                parent=normal,
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#334155'),
                spaceAfter=6
            )

            story = []

            idea = state.idea
            report = state.final_report

            # Document Title
            story.append(Paragraph("AI Startup Idea Validation Report", title_style))
            story.append(Paragraph(f"<b>Concept:</b> {idea.idea_text}<br/><b>Industry:</b> {idea.target_industry} | <b>Audience:</b> {idea.target_audience}", subtitle_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=15))

            if report:
                # Executive Summary Box
                verdict_color = "#16A34A" if report.verdict == "PROCEED" else ("#CA8A04" if report.verdict in ["PIVOT", "CAUTION"] else "#DC2626")
                
                score_table_data = [
                    [
                        Paragraph(f"<font size=16 color='{verdict_color}'><b>{report.overall_viability_score}/100</b></font><br/>Overall Score", body_style),
                        Paragraph(f"<font size=14 color='{verdict_color}'><b>VERDICT: {report.verdict}</b></font>", body_style)
                    ]
                ]
                t = Table(score_table_data, colWidths=[150, 350])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0,0), (-1,-1), 10),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                story.append(t)
                story.append(Spacer(1, 15))

                story.append(Paragraph("Executive Summary", h2_style))
                story.append(Paragraph(report.executive_summary, body_style))
                story.append(Spacer(1, 10))

            # Market Analysis
            if state.market_analysis:
                m = state.market_analysis
                story.append(Paragraph("1. Market Analysis", h2_style))
                story.append(Paragraph(f"<b>TAM:</b> ${m.tam_billions}B | <b>SAM:</b> ${m.sam_billions}B | <b>SOM:</b> ${m.som_billions}B | <b>CAGR:</b> {m.cagr_percentage}%", body_style))
                story.append(Paragraph(m.market_size_summary, body_style))
                story.append(Spacer(1, 10))

            # Competitor Analysis
            if state.competitor_analysis:
                c = state.competitor_analysis
                story.append(Paragraph("2. Competitor Analysis & Moat", h2_style))
                story.append(Paragraph(f"<b>Positioning:</b> {c.market_positioning_summary}", body_style))
                story.append(Paragraph(f"<b>Competitive Moat:</b> {c.moat_assessment}", body_style))
                story.append(Spacer(1, 10))

            # SWOT
            if state.swot_analysis:
                s = state.swot_analysis
                story.append(Paragraph("3. SWOT & Risk Assessment", h2_style))
                story.append(Paragraph(f"<b>Strengths:</b> {', '.join(s.strengths)}", body_style))
                story.append(Paragraph(f"<b>Weaknesses:</b> {', '.join(s.weaknesses)}", body_style))
                story.append(Paragraph(f"<b>Opportunities:</b> {', '.join(s.opportunities)}", body_style))
                story.append(Paragraph(f"<b>Threats:</b> {', '.join(s.threats)}", body_style))
                story.append(Spacer(1, 10))

            doc.build(story)
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            return None
