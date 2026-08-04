import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional
from state.schema import StartupState, ValidationReport, ScoringBreakdown


class ChartEngine:
    """Plotly Data Visualization Engine for Enterprise Startup Decision Support."""

    @staticmethod
    def render_viability_gauge(score: int, title: str = "Overall Viability Score") -> go.Figure:
        """Renders an interactive 0-100 Gauge Chart."""
        color = "#22C55E" if score >= 78 else ("#F59E0B" if score >= 65 else "#EF4444")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': title, 'font': {'size': 18, 'color': '#0F172A', 'family': 'Inter'}},
            number={'font': {'size': 44, 'color': color, 'family': 'Inter', 'weight': 'bold'}, 'suffix': "/100"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#CBD5E1"},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E2E8F0",
                'steps': [
                    {'range': [0, 50], 'color': '#FEE2E2'},
                    {'range': [50, 75], 'color': '#FEF3C7'},
                    {'range': [75, 100], 'color': '#DCFCE7'}
                ]
            }
        ))
        fig.update_layout(
            height=280,
            margin=dict(l=30, r=30, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @staticmethod
    def render_scoring_matrix_bar(scoring: ScoringBreakdown) -> go.Figure:
        """Renders an 8-Dimension Weighted Score Matrix Bar Chart."""
        categories = [
            'Market Opportunity', 'Innovation', 'Competition', 'Scalability',
            'Tech Feasibility', 'Revenue Model', 'Execution Risk', 'Market Timing'
        ]
        scores = [
            scoring.market_opportunity_score, scoring.innovation_score,
            scoring.competition_score, scoring.scalability_score,
            scoring.technical_feasibility_score, scoring.revenue_model_score,
            scoring.execution_risk_score, scoring.market_timing_score
        ]
        max_scores = [20, 15, 15, 15, 10, 10, 10, 5]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories,
            y=scores,
            name="Score Achieved",
            marker_color="#2563EB",
            text=[f"{s}/{m}" for s, m in zip(scores, max_scores)],
            textposition='auto',
        ))

        fig.update_layout(
            title={'text': "8-Dimension Weighted Scoring Matrix Breakdown", 'font': {'size': 16, 'family': 'Inter'}},
            xaxis={'title': None},
            yaxis={'title': 'Score Points', 'range': [0, 22]},
            height=320,
            margin=dict(l=30, r=30, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @staticmethod
    def render_scoring_radar(scoring: ScoringBreakdown) -> go.Figure:
        """Renders an 8-Dimension Radar Chart normalized to 100% per dimension."""
        categories = [
            'Market Opp', 'Innovation', 'Competition', 'Scalability',
            'Tech Feasibility', 'Revenue Model', 'Risk Resilience', 'Market Timing'
        ]
        normalized = [
            (scoring.market_opportunity_score / 20.0) * 100,
            (scoring.innovation_score / 15.0) * 100,
            (scoring.competition_score / 15.0) * 100,
            (scoring.scalability_score / 15.0) * 100,
            (scoring.technical_feasibility_score / 10.0) * 100,
            (scoring.revenue_model_score / 10.0) * 100,
            (scoring.execution_risk_score / 10.0) * 100,
            (scoring.market_timing_score / 5.0) * 100
        ]

        categories.append(categories[0])
        normalized.append(normalized[0])

        fig = go.Figure(go.Scatterpolar(
            r=normalized,
            theta=categories,
            fill='toself',
            fillcolor='rgba(37, 99, 235, 0.25)',
            line=dict(color='#2563EB', width=2),
            name="Viability Profile"
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            title={'text': "Strategic Dimension Radar Profile", 'font': {'size': 16, 'family': 'Inter'}},
            height=340,
            margin=dict(l=40, r=40, t=50, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @staticmethod
    def render_market_growth_trajectory(tam: float, cagr: float) -> go.Figure:
        """Renders 5-Year CAGR Market Sizing Growth Projection Line Chart."""
        years = [f"Year {i}" for i in range(1, 6)]
        values = [round(tam * ((1 + (cagr / 100.0)) ** i), 2) for i in range(5)]

        fig = go.Figure(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            line=dict(color='#7C3AED', width=3),
            marker=dict(size=8, color='#06B6D4'),
            fill='tozeroy',
            fillcolor='rgba(124, 58, 237, 0.1)'
        ))

        fig.update_layout(
            title={'text': f"5-Year Project Market Growth Trajectory (TAM ${tam}B @ {cagr}% CAGR)", 'font': {'size': 15, 'family': 'Inter'}},
            yaxis={'title': 'Market Volume ($ Billions)'},
            height=300,
            margin=dict(l=30, r=30, t=50, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @staticmethod
    def render_risk_severity_pie(fin_risk: int, tech_risk: int, reg_risk: int) -> go.Figure:
        """Renders a Risk Category Breakdown Pie Chart."""
        labels = ['Financial Risk', 'Technical Risk', 'Regulatory & Market Risk']
        values = [fin_risk, tech_risk, reg_risk]
        colors = ['#EF4444', '#F59E0B', '#2563EB']

        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.45,
            marker_colors=colors,
            textinfo='label+percent'
        ))

        fig.update_layout(
            title={'text': "Categorized Risk Severity Breakdown", 'font': {'size': 15, 'family': 'Inter'}},
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
