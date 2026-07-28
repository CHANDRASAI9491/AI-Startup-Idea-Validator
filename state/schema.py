from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class StartupIdea(BaseModel):
    idea_text: str = Field(..., description="Description of the startup idea")
    target_industry: Optional[str] = Field(default="Technology", description="Industry sector")
    target_audience: Optional[str] = Field(default="General Users / Businesses", description="Target market")
    budget: Optional[str] = Field(default="Bootstrap ($5k - $50k)", description="Estimated initial budget")
    timeline: Optional[str] = Field(default="3 Months", description="Target launch timeline")


class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str


class WebSearchResults(BaseModel):
    market_trends: List[SearchResultItem] = Field(default_factory=list)
    competitors: List[SearchResultItem] = Field(default_factory=list)
    customer_pain_points: List[SearchResultItem] = Field(default_factory=list)
    industry_news: List[SearchResultItem] = Field(default_factory=list)
    funding: List[SearchResultItem] = Field(default_factory=list)


class TargetPersona(BaseModel):
    role: str
    pain_points: List[str]
    willingness_to_pay: str


class MarketAnalysis(BaseModel):
    tam_billions: float = Field(default=10.0, description="Total Addressable Market in $B")
    sam_billions: float = Field(default=2.5, description="Serviceable Addressable Market in $B")
    som_billions: float = Field(default=0.1, description="Serviceable Obtainable Market in $B")
    market_size_summary: str = Field(default="", description="Summary of market scope and numbers")
    cagr_percentage: float = Field(default=12.5, description="Compound Annual Growth Rate %")
    key_growth_drivers: List[str] = Field(default_factory=list)
    target_personas: List[TargetPersona] = Field(default_factory=list)
    market_readiness_score: int = Field(default=75, description="0-100 Market Readiness score")


class CompetitorItem(BaseModel):
    name: str
    url: str = ""
    description: str = ""
    key_features: List[str] = Field(default_factory=list)
    pricing_model: str = "Freemium / Subscription"
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class CompetitorAnalysis(BaseModel):
    direct_competitors: List[CompetitorItem] = Field(default_factory=list)
    indirect_competitors: List[CompetitorItem] = Field(default_factory=list)
    feature_comparison_matrix: Dict[str, Any] = Field(default_factory=dict)
    market_positioning_summary: str = ""
    moat_assessment: str = ""


class SWOTAnalysis(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)
    financial_risk: int = Field(default=5, description="Risk level 1-10")
    technical_risk: int = Field(default=5, description="Risk level 1-10")
    regulatory_risk: int = Field(default=4, description="Risk level 1-10")
    overall_risk_score: int = Field(default=5, description="0-10 Overall Risk")
    risk_mitigation_plan: List[str] = Field(default_factory=list)


class MVPFeature(BaseModel):
    feature_name: str
    priority: str = "Must Have"  # Must Have, Should Have, Could Have
    estimated_days: int = 5
    description: str = ""


class MVPRecommendation(BaseModel):
    core_value_proposition: str = ""
    tech_stack_frontend: str = "React / Next.js"
    tech_stack_backend: str = "FastAPI (Python)"
    tech_stack_database: str = "PostgreSQL"
    tech_stack_ai: str = "Google Gemini API"
    features: List[MVPFeature] = Field(default_factory=list)
    four_week_roadmap: Dict[str, str] = Field(default_factory=dict)
    key_metrics_kpis: List[str] = Field(default_factory=list)


class GTMStrategy(BaseModel):
    primary_acquisition_channels: List[str] = Field(default_factory=list)
    pricing_strategy: str = ""
    positioning_statement: str = ""
    launch_tactics: List[str] = Field(default_factory=list)
    estimated_cac_summary: str = ""


class ValidationReport(BaseModel):
    overall_viability_score: int = Field(..., description="0-100 overall score")
    verdict: str = Field(..., description="PROCEED, PIVOT, CAUTION, or STOP")
    executive_summary: str
    market_score: int = 75
    competitor_score: int = 70
    risk_score: int = 80
    mvp_score: int = 85
    gtm_score: int = 75
    key_takeaways: List[str] = Field(default_factory=list)
    recommended_next_steps: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class AgentState(BaseModel):
    idea: StartupIdea
    search_results: Optional[WebSearchResults] = None
    market_analysis: Optional[MarketAnalysis] = None
    competitor_analysis: Optional[CompetitorAnalysis] = None
    swot_analysis: Optional[SWOTAnalysis] = None
    mvp_recommendation: Optional[MVPRecommendation] = None
    gtm_strategy: Optional[GTMStrategy] = None
    final_report: Optional[ValidationReport] = None
    status: str = "initialized"
    error: Optional[str] = None
