import plotly.graph_objects as go
from typing import List, Dict, Any
from services.scoring_engine import ScoringBreakdown


def render_startup_score_gauge(score: int, verdict: str) -> go.Figure:
    """Builds Viability Index Gauge Indicator Chart."""
    gauge_color = "#166534" if verdict == "PROCEED" else ("#854D0E" if verdict in ["PIVOT", "CAUTION"] else "#991B1B")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Viability Index ({verdict})", 'font': {'size': 16, 'color': '#0F172A'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': gauge_color},
            'bgcolor': "#FFFFFF",
            'borderwidth': 1,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [0, 60], 'color': '#FEE2E2'},
                {'range': [60, 75], 'color': '#FEF08A'},
                {'range': [75, 100], 'color': '#DCFCE7'}
            ]
        }
    ))
    fig.update_layout(
        font=dict(family="-apple-system, system-ui, sans-serif", color="#0F172A"),
        height=240,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="#FFFFFF"
    )
    return fig


def render_8dimension_score_breakdown_chart(scoring: ScoringBreakdown) -> go.Figure:
    """Builds 8-Dimension Weighted Score Matrix Bar Chart."""
    categories = [
        "Market Opp (20)", "Innovation (15)", "Competition (15)",
        "Scalability (15)", "Tech Feasibility (10)", "Revenue Model (10)",
        "Risk Resilience (10)", "Timing (5)"
    ]
    scores = [
        scoring.market_opportunity_score, scoring.innovation_score, scoring.competition_score,
        scoring.scalability_score, scoring.technical_feasibility_score, scoring.revenue_model_score,
        scoring.execution_risk_score, scoring.market_timing_score
    ]
    max_scores = [20, 15, 15, 15, 10, 10, 10, 5]

    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=scores,
            marker_color=["#2563EB", "#7C3AED", "#06B6D4", "#14B8A6", "#0284C7", "#059669", "#D97706", "#F97316"],
            text=[f"{s}/{m}" for s, m in zip(scores, max_scores)],
            textposition="auto"
        )
    ])
    fig.update_layout(
        title="8-Dimension Weighted Score Matrix Breakdown (Total: 100)",
        font=dict(family="-apple-system, system-ui, sans-serif", color="#0F172A"),
        template="plotly_white",
        yaxis=dict(title="Calculated Weighted Score"),
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC"
    )
    return fig


def render_market_growth_line_chart(tam: float, sam: float, som: float, cagr: float) -> go.Figure:
    """Builds Market Growth Line Chart projecting 5-year growth trajectory."""
    years = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    growth_rate = max(cagr, 5.0) / 100.0
    som_vals = [round(som * ((1 + growth_rate) ** i), 2) for i in range(5)]
    sam_vals = [round(sam * ((1 + growth_rate * 0.5) ** i), 2) for i in range(5)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=sam_vals, mode='lines+markers', name='SAM Trajectory ($B)',
        line=dict(color='#7C3AED', width=3), marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=years, y=som_vals, mode='lines+markers', name='SOM Trajectory ($B)',
        line=dict(color='#2563EB', width=3), marker=dict(size=8)
    ))
    fig.update_layout(
        title=f"Projected Market Trajectory ({cagr}% CAGR)",
        font=dict(family="-apple-system, system-ui, sans-serif", color="#0F172A"),
        template="plotly_white",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        yaxis=dict(title="Market Volume ($ Billions)")
    )
    return fig


def render_swot_radar_chart(strengths_n: int, opps_n: int, threats_n: int, weak_n: int) -> go.Figure:
    """Builds SWOT Radar Chart."""
    categories = ["Strengths", "Opportunities", "Threats", "Weaknesses"]
    values = [max(strengths_n, 1), max(opps_n, 1), max(threats_n, 1), max(weak_n, 1)]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='SWOT Dimensions',
        line_color='#2563EB',
        fillcolor='rgba(37, 99, 235, 0.15)'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(values) + 2])
        ),
        title="SWOT Strategic Balance Index",
        font=dict(family="-apple-system, system-ui, sans-serif", color="#0F172A"),
        template="plotly_white",
        height=320,
        margin=dict(l=40, r=40, t=40, b=20),
        paper_bgcolor="#FFFFFF"
    )
    return fig


def render_risk_distribution_pie_chart(financial: int, technical: int, regulatory: int) -> go.Figure:
    """Builds Risk Distribution Pie Chart."""
    labels = ["Financial Risk", "Technical Risk", "Regulatory Risk"]
    values = [financial, technical, regulatory]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=["#DC2626", "#EA580C", "#D97706"])
    )])
    fig.update_layout(
        title="Risk Severity Distribution",
        font=dict(family="-apple-system, system-ui, sans-serif", color="#0F172A"),
        template="plotly_white",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#FFFFFF"
    )
    return fig


def render_competitor_comparison_chart(competitor_names: List[str], strengths_count: List[int]) -> go.Figure:
    """Builds Competitor Comparison Bar Chart."""
    fig = go.Figure(data=[
        go.Bar(
            x=competitor_names,
            y=strengths_count,
            marker_color="#7C3AED",
            text=[f"{c} Strengths" for c in strengths_count],
            textposition="auto"
        )
    ])
    fig.update_layout(
        title="Competitor Market Strengths Comparison",
        font=dict(family="-apple-system, system-ui, sans-serif", color="#0F172A"),
        template="plotly_white",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC"
    )
    return fig
