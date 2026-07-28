import os
import json
from typing import Dict, Any
from state.schema import AgentState


class FileTools:

    @staticmethod
    def export_report_markdown(state: AgentState, output_path: str) -> str:
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
            f"**Overall Viability Score:** {report.overall_viability_score}/100",
            f"**Verdict:** `{report.verdict}`",
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
    def export_report_json(state: AgentState, output_path: str) -> None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))
