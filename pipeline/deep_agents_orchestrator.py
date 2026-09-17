import logging
import json
import re
from typing import Callable, Optional, List, Dict, Any, Tuple
from deepagents import create_deep_agent, SubAgent  # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
from langchain_core.messages import AIMessage  # type: ignore

from state.schema import (
    StartupState,
    StartupIdea,
    DeepAgentsPlan,
    MarketAnalysis,
    CompetitorAnalysis,
    SWOTAnalysis,
    MVPRecommendation,
    GTMStrategy,
    ValidationReport,
    TargetPersona,
    CompetitorItem,
    RiskItem,
    MVPFeature
)
from tools.planning_tool import DeepAgentsPlanner
from tools.tavily_tool import tavily_search_tool, TavilySearchTool
from tools.retrieval_utils import format_search_results_summary
from agents.market_analysis_agent import MarketAnalysisAgent
from agents.competitor_agent import CompetitorAgent
from agents.swot_risk_agent import SWOTRiskAgent
from agents.mvp_recommendation_agent import MVPRecommendationAgent
from agents.gtm_strategy_agent import GTMStrategyAgent
from agents.report_agent import ReportAgent
from services.scoring_engine import DeterministicScoringEngine
from app.config import config
from services.logger import get_logger

logger = get_logger(__name__)


def _clean_markdown_line(line: str) -> str:
    """Strips markdown bold/italic formatting characters from line."""
    return re.sub(r'[*_`]', '', line)


def _extract_text_from_content(content: Any) -> str:
    """Safely extracts plain text from either a string or a list of message content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block and isinstance(block["text"], str):
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return ""


def _parse_currency_to_billions(amount_str: str) -> Optional[float]:
    """Generic unit-aware converter for currency amounts to billions ($B).
    Supports Trillion (T), Billion (B), Million (M).
    Returns float rounded to 4 decimal places, or None if unparseable.
    Never invents or estimates values.
    """
    if not amount_str:
        return None

    clean = re.sub(r'[\$,~≈]', '', amount_str).strip()
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(trillion|billion|million|[tbm])\b', clean, re.IGNORECASE)
    if not match:
        return None

    num_val = float(match.group(1))
    unit = match.group(2).lower()

    if unit in ('trillion', 't'):
        return round(num_val * 1000.0, 4)
    elif unit in ('billion', 'b'):
        return round(num_val, 4)
    elif unit in ('million', 'm'):
        return round(num_val / 1000.0, 4)
    return None


def _extract_market_metric(text: str, metric_name: str) -> Optional[float]:
    """Finds a metric like TAM, SAM, or SOM in text and converts its value to billions."""
    for line in text.splitlines():
        clean_line = _clean_markdown_line(line)
        metric_match = re.search(rf'\b{metric_name}\b', clean_line, re.IGNORECASE)
        if metric_match:
            pattern = rf'\b{metric_name}\b[^\n\r:]*[:\s–—\-]+[~≈]?\s*(\$?\s*[0-9]+(?:\.[0-9]+)?\s*(?:trillion|billion|million|[tbm])\b)'
            match = re.search(pattern, clean_line, re.IGNORECASE)
            if match:
                val = _parse_currency_to_billions(match.group(1))
                if val is not None:
                    return val
            after_metric = clean_line[metric_match.end():]
            curr_match = re.search(r'(\$?\s*[0-9]+(?:\.[0-9]+)?\s*(?:trillion|billion|million|[tbm])\b)', after_metric, re.IGNORECASE)
            if curr_match:
                val = _parse_currency_to_billions(curr_match.group(1))
                if val is not None:
                    return val
    return None


def _parse_cagr(text: str) -> Optional[float]:
    """Extracts CAGR percentage from text.
    If CAGR is a range (e.g. '12.6%–16.9% CAGR'), returns None per requirement.
    If CAGR is a single float (e.g. '14.5% CAGR'), returns that float.
    """
    if not text:
        return None

    # 1. Check for range: e.g. "12.6%–16.9% CAGR", "12.6% - 16.9% CAGR", "CAGR of 12.6% to 16.9%"
    range_pattern = r'([0-9]+(?:\.[0-9]+)?)\s*%\s*[-–—to]+\s*([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:projected\s+)?CAGR\b|CAGR\b[^\n\r]*?([0-9]+(?:\.[0-9]+)?)\s*%\s*[-–—to]+\s*([0-9]+(?:\.[0-9]+)?)\s*%'
    if re.search(range_pattern, text, re.IGNORECASE):
        return None

    # 2. Check for single percentage CAGR: e.g. "14.5% CAGR", "CAGR of 15%", "CAGR: 13.6%"
    single_pattern = r'([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:projected\s+)?CAGR\b|CAGR\b[^\n\r:]*?[:\s–—\-]+([0-9]+(?:\.[0-9]+)?)\s*%'
    match = re.search(single_pattern, text, re.IGNORECASE)
    if match:
        val_str = match.group(1) or match.group(2)
        try:
            return float(val_str)
        except (ValueError, TypeError):
            return None

    return None


def _extract_section_text(markdown: str, section_keywords: List[str]) -> str:
    """Extracts lines under a heading matching any of section_keywords until the next major section."""
    lines = markdown.splitlines()
    capturing = False
    captured_lines = []
    captured_heading_level = 0

    for line in lines:
        stripped = line.strip()
        heading_match = re.match(r'^(#{1,6})\s*(.*)', stripped)
        bold_heading_match = re.match(r'^\*{2}\s*(.*?)\s*\*{2}\s*$', stripped) if not heading_match else None

        current_level = 0
        heading_title = ""
        if heading_match:
            current_level = len(heading_match.group(1))
            heading_title = heading_match.group(2).strip()
        elif bold_heading_match:
            current_level = 3
            heading_title = bold_heading_match.group(1).strip()

        if heading_title:
            matches_target = any(
                re.search(rf'\b{kw}\b', heading_title, re.IGNORECASE)
                for kw in section_keywords
            )

            if not capturing:
                if matches_target:
                    capturing = True
                    captured_heading_level = current_level
                    continue
            else:
                # Subsections within the target section: deeper heading level or lettered sub-heading (e.g. A. Direct Incumbents)
                is_sub = (
                    current_level > captured_heading_level
                    or bool(re.match(r'^[A-Za-z][\.\)]\s+', heading_title))
                )
                if is_sub:
                    captured_lines.append(line)
                    continue
                else:
                    # Reached next sibling or higher-level major section
                    break
        elif capturing:
            captured_lines.append(line)

    return "\n".join(captured_lines).strip()


def _parse_market_analysis_from_markdown(markdown: str) -> Optional[MarketAnalysis]:
    """Safely extracts MarketAnalysis from Markdown validation report."""
    if not markdown:
        return None

    market_section = _extract_section_text(markdown, ["Market Research", "Market Sizing", "Market Analysis", "Market"])
    text_to_search = market_section if market_section else markdown

    tam = _extract_market_metric(text_to_search, "TAM")
    sam = _extract_market_metric(text_to_search, "SAM")
    som = _extract_market_metric(text_to_search, "SOM")
    cagr = _parse_cagr(text_to_search)

    growth_drivers = []
    drivers_match = re.search(r'\b(?:Key\s+)?Growth\s+Drivers\b[^\n\r:]*[:\s–—\-]+([^\n\r]+)', _clean_markdown_line(text_to_search), re.IGNORECASE)
    if drivers_match:
        raw_drivers = drivers_match.group(1).strip()
        growth_drivers = [d.strip(' .;') for d in re.split(r'[,;]|(?:\sand\s)', raw_drivers) if d.strip(' .;')]

    if market_section:
        summary_lines = []
        for line in market_section.splitlines():
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            clean = _clean_markdown_line(s)
            if re.search(r'^(?:TAM|SAM|SOM|CAGR)\b', clean, re.IGNORECASE):
                continue
            summary_lines.append(clean)
        market_summary = " ".join(summary_lines)[:500].strip()
        if not market_summary:
            if tam is not None:
                market_summary = f"Target Market TAM of ${tam}B established from executive research report."
            else:
                market_summary = "Market size could not be established from available research."
    elif tam is not None:
        market_summary = f"Target Market TAM of ${tam}B established from executive research report."
    else:
        market_summary = "Market size could not be established from available research."

    if tam is None and sam is None and som is None and cagr is None and not growth_drivers and (not market_section or market_summary == "Market size could not be established from available research."):
        return None

    return MarketAnalysis(
        tam_billions=tam,
        sam_billions=sam,
        som_billions=som,
        market_size_summary=market_summary,
        cagr_percentage=cagr,
        key_growth_drivers=growth_drivers,
        target_personas=[]
    )


def _clean_competitor_name(raw: str) -> Tuple[str, str]:
    """Cleans a raw competitor token and extracts optional description from parentheses.
    Never splits on slashes inside parentheses, preserving expressions like (Pulse AI / Signals).
    """
    raw = _clean_markdown_line(raw).strip(' .-,;:\t*')
    m = re.search(r'^(.*?)\s*\((.*?)\)$', raw)
    if m:
        name = m.group(1).strip(' .-,;:\t*')
        desc = m.group(2).strip(' .-,;:\t*')
        return name, desc
    return raw, ""


def _parse_competitor_analysis_from_markdown(markdown: str) -> Optional[CompetitorAnalysis]:
    """Safely and generically extracts CompetitorAnalysis from Markdown validation report."""
    if not markdown:
        return None

    # Step 1: Isolate competitor / competitive landscape section if present
    comp_keywords = [
        "Competitor Landscape",
        "Competitive Landscape",
        "Competitor Research",
        "Competitive Research",
        "Competitor Analysis",
        "Competitive Analysis",
        "Competitors",
        "Competition"
    ]
    comp_section = _extract_section_text(markdown, comp_keywords)

    # Search within competitor section to protect against capturing unrelated company names
    text_to_search = comp_section if comp_section else markdown

    direct_items: List[CompetitorItem] = []
    indirect_items: List[CompetitorItem] = []
    seen_direct = set()
    seen_indirect = set()

    def add_direct(name: str, desc: str = ""):
        name = name.strip(' .-,;:\t*')
        if not name or len(name) < 2 or len(name) > 80:
            return
        if name.lower() in ("the gap", "market", "overview", "summary", "pricing", "features", "strengths", "weaknesses"):
            return
        if name.lower() not in seen_direct:
            seen_direct.add(name.lower())
            direct_items.append(CompetitorItem(name=name, description=desc))

    def add_indirect(name: str, desc: str = ""):
        name = name.strip(' .-,;:\t*')
        if not name or len(name) < 2 or len(name) > 120:
            return
        if name.lower() in ("the gap", "market", "overview", "summary", "pricing", "features"):
            return
        if name.lower() not in seen_indirect and name.lower() not in seen_direct:
            seen_indirect.add(name.lower())
            indirect_items.append(CompetitorItem(name=name, description=desc))

    # Pattern 1: Inline lists with explicit Direct Competitor / Incumbent label
    # e.g. * **Direct Competitors:** Reviewflowz, FeedCheck, RightResponse AI, Yotpo (e-commerce specific).
    direct_line_pattern = re.compile(
        r'(?:^|\n)[*\s–—\-0-9.]*\**\b(Direct\s+Competitors?|Direct\s+Incumbents?|Direct\s+Alternatives?|Enterprise\s+Incumbents?|Incumbents?)\b\**\s*[:–—\-]\s*([^\n\r]+)',
        re.IGNORECASE
    )
    for m in direct_line_pattern.finditer(text_to_search):
        raw_list = m.group(2).strip()
        tokens = [t.strip() for t in re.split(r'[,;]', raw_list) if t.strip()]
        for token in tokens:
            name, desc = _clean_competitor_name(token)
            add_direct(name, desc)

    # Pattern 2: Inline lists with explicit Indirect Competitor / Substitute label
    # e.g. * **Indirect Status Quo:** Manual CSV exports into ChatGPT or spreadsheets.
    indirect_line_pattern = re.compile(
        r'(?:^|\n)[*\s–—\-0-9.]*\**\b(Indirect\s+Competitors?|Indirect\s+Substitutes?|Indirect\s+Alternatives?|Indirect\s+Status\s+Quo|Indirect)\b\**\s*[:–—\-]\s*([^\n\r]+)',
        re.IGNORECASE
    )
    for m in indirect_line_pattern.finditer(text_to_search):
        raw_list = m.group(2).strip()
        tokens = [t.strip() for t in re.split(r'[,;]', raw_list) if t.strip()]
        if len(tokens) <= 1:
            name, desc = _clean_competitor_name(raw_list)
            add_indirect(name, desc)
        else:
            for token in tokens:
                name, desc = _clean_competitor_name(token)
                add_indirect(name, desc)

    # Pattern 3: Subsections with bulleted/numbered items under Direct vs Indirect
    # e.g. ### A. Direct Incumbents (SMB Review Management & AI Sentiment)
    #      * **RightResponse AI / RightResponse Competitor Review Analysis:** ...
    # Only triggered when actual heading lines with # define the subsection!
    current_mode = None
    for line in text_to_search.splitlines():
        clean_l = line.strip()
        if not clean_l:
            continue

        if clean_l.startswith('#'):
            h_text = _clean_markdown_line(clean_l).lstrip('#').strip()
            if re.search(r'\b(?:Direct\s+Incumbents?|Direct\s+Competitors?|Direct\s+Alternatives?|Enterprise\s+Incumbents?)\b', h_text, re.IGNORECASE):
                current_mode = "direct"
            elif re.search(r'\b(?:Indirect\s+Substitutes?|Indirect\s+Competitors?|Indirect\s+Alternatives?|Substitutes?)\b', h_text, re.IGNORECASE):
                current_mode = "indirect"
            else:
                current_mode = None
            continue

        if current_mode in ("direct", "indirect"):
            item_match = re.match(r'^[*\s–—\-0-9.]*\**([^*:\n\r–—\-]+)\**\s*[:–—\-]\s*(.*)', clean_l)
            if item_match:
                raw_name = item_match.group(1).strip()
                desc = _clean_markdown_line(item_match.group(2)).strip()

                if raw_name.lower() in ("direct competitors", "indirect competitors", "defensibility moat", "market positioning", "the gap", "pricing"):
                    continue

                # Handle / separated company names while preserving parentheticals like (Pulse AI / Signals)
                if '/' in raw_name and not re.search(r'\(.*\/.*\)', raw_name):
                    parts = [p.strip() for p in raw_name.split('/') if p.strip()]
                    if all(len(p) < 40 for p in parts):
                        for p in parts:
                            c_name, c_desc = _clean_competitor_name(p)
                            if current_mode == "direct":
                                add_direct(c_name, desc)
                            else:
                                add_indirect(c_name, desc)
                        continue
                    else:
                        raw_name = parts[0]

                c_name, c_desc = _clean_competitor_name(raw_name)
                final_desc = desc if desc else c_desc
                if current_mode == "direct":
                    add_direct(c_name, final_desc)
                else:
                    add_indirect(c_name, final_desc)

    # Pattern 4: Narrative mentions in competitor section with category labels and parenthesized company names
    # e.g. Enterprise CX tools (Qualtrics, Medallia) are too expensive ...
    #      Traditional review tools (Podium, Birdeye) focus heavily ...
    if not direct_items and comp_section:
        ent_match = re.search(r'\b(?:Enterprise\s+(?:CX\s+)?tools?|Direct\s+(?:tools?|competitors?|incumbents?)|Incumbents?)\s*\(([^)]+)\)', comp_section, re.IGNORECASE)
        if ent_match:
            for token in ent_match.group(1).split(','):
                name, desc = _clean_competitor_name(token)
                add_direct(name, desc)

    if not indirect_items and comp_section:
        trad_match = re.search(r'\b(?:Traditional\s+(?:review\s+)?tools?|Indirect\s+(?:tools?|substitutes?|alternatives?)|Substitutes?)\s*\(([^)]+)\)', comp_section, re.IGNORECASE)
        if trad_match:
            for token in trad_match.group(1).split(','):
                name, desc = _clean_competitor_name(token)
                add_indirect(name, desc)

    # Step 5: Market Positioning Summary Extraction
    pos_summary = ""
    pos_line_pattern = re.compile(
        r'(?:^|\n)[*\s–—\-0-9.]*\**\b(Market\s+Positioning|Positioning\s+Statement|Positioning|Our\s+Competitive\s+Edge)\b\**\s*[:–—\-]\s*([^\n\r]+)',
        re.IGNORECASE
    )
    p_match = pos_line_pattern.search(text_to_search)
    if p_match:
        pos_summary = _clean_markdown_line(p_match.group(2)).strip(' "“\'')

    if not pos_summary and text_to_search != markdown:
        p_match_full = pos_line_pattern.search(markdown)
        if p_match_full:
            pos_summary = _clean_markdown_line(p_match_full.group(2)).strip(' "“\'')

    if not pos_summary and comp_section:
        gap_match = re.search(r'(?:^|\n)[*\s–—\-0-9.]*\**\b(The\s+Gap)\b\**\s*[:–—\-]\s*([^\n\r]+)', comp_section, re.IGNORECASE)
        if gap_match:
            pos_summary = _clean_markdown_line(gap_match.group(2)).strip()
        else:
            first_p = [l.strip() for l in comp_section.splitlines() if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('*')][:1]
            if first_p:
                pos_summary = _clean_markdown_line(first_p[0])[:300].strip()

    # Step 6: Moat Assessment Extraction
    # CRITICAL: Separator MUST require a colon or dash, NEVER arbitrary whitespace!
    moat_assessment = ""
    moat_line_pattern = re.compile(
        r'(?:^|\n)[*\s–—\-0-9.]*\**\b(Defensibility\s+Moat|Competitive\s+Moat|Defensible\s+Niche|Competitive\s+Advantage|Competitive\s+Edge|Moat\s+Assessment|Defensibility|Moat)\b\**\s*[:–—\-]\s*\**\s*([^\n\r]+)',
        re.IGNORECASE
    )

    if comp_section:
        m_match = moat_line_pattern.search(comp_section)
        if m_match:
            candidate = _clean_markdown_line(m_match.group(2)).strip(' .-,;:\t')
            if len(candidate) > 15 and not candidate.endswith(')') and not re.match(r'^[A-Za-z0-9\s]+\)$', candidate):
                moat_assessment = candidate

    if not moat_assessment:
        moat_section = _extract_section_text(markdown, ["Defensibility Moats", "Defensibility Moat", "Competitive Moats", "Defensibility", "Moats", "Moat"])
        if moat_section:
            m_match = moat_line_pattern.search(moat_section)
            if m_match:
                candidate = _clean_markdown_line(m_match.group(2)).strip(' .-,;:\t')
                if len(candidate) > 15 and not re.match(r'^[A-Za-z0-9\s]+\)$', candidate):
                    moat_assessment = candidate
            else:
                first_lines = [l.strip() for l in moat_section.splitlines() if l.strip() and not l.strip().startswith('#')][:2]
                if first_lines:
                    moat_assessment = _clean_markdown_line(" ".join(first_lines))[:400].strip()

    if not moat_assessment:
        for m in moat_line_pattern.finditer(markdown):
            candidate = _clean_markdown_line(m.group(2)).strip(' .-,;:\t')
            if len(candidate) > 15 and not re.match(r'^[A-Za-z0-9\s]+\)$', candidate):
                moat_assessment = candidate
                break

    if not direct_items and not indirect_items and not pos_summary and not moat_assessment:
        return None

    return CompetitorAnalysis(
        direct_competitors=direct_items,
        indirect_competitors=indirect_items,
        market_positioning_summary=pos_summary or "No verified competitors identified from available research.",
        moat_assessment=moat_assessment or "Defensibility cannot be evaluated without verified competitor evidence."
    )



def _parse_swot_analysis_from_markdown(markdown: str) -> Optional[SWOTAnalysis]:
    """Safely extracts SWOTAnalysis from Markdown report."""
    swot_text = _extract_section_text(markdown, ["SWOT", "Risk Management"])
    if not swot_text:
        return None

    clean = _clean_markdown_line(swot_text)
    strengths, weaknesses, opportunities, threats = [], [], [], []

    for line in clean.splitlines():
        if re.search(r'\bStrengths\b', line, re.IGNORECASE):
            match = re.search(r'\bStrengths\b[^\n\r:]*[:\s–—\-]+([^\n\r]+)', line, re.IGNORECASE)
            if match:
                strengths = [s.strip(' .;') for s in re.split(r'[,;]', match.group(1)) if s.strip(' .;')]
        elif re.search(r'\bWeaknesses\b', line, re.IGNORECASE):
            match = re.search(r'\bWeaknesses\b[^\n\r:]*[:\s–—\-]+([^\n\r]+)', line, re.IGNORECASE)
            if match:
                weaknesses = [w.strip(' .;') for w in re.split(r'[,;]', match.group(1)) if w.strip(' .;')]
        elif re.search(r'\bOpportunities\b', line, re.IGNORECASE):
            match = re.search(r'\bOpportunities\b[^\n\r:]*[:\s–—\-]+([^\n\r]+)', line, re.IGNORECASE)
            if match:
                opportunities = [o.strip(' .;') for o in re.split(r'[,;]', match.group(1)) if o.strip(' .;')]
        elif re.search(r'\b(?:Threats|Top\s+Risk)\b', line, re.IGNORECASE):
            match = re.search(r'\b(?:Threats|Top\s+Risk(?:[^\n\r:]*)?)\b[^\n\r:]*[:\s–—\-]+([^\n\r]+)', line, re.IGNORECASE)
            if match:
                threats = [t.strip(' .;') for t in re.split(r'[,;]', match.group(1)) if t.strip(' .;')]

    if not strengths and not weaknesses and not opportunities and not threats:
        return None

    return SWOTAnalysis(
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
        threats=threats
    )


def _parse_mvp_recommendation_from_markdown(markdown: str) -> Optional[MVPRecommendation]:
    """Safely extracts MVPRecommendation from Markdown report."""
    mvp_text = _extract_section_text(markdown, ["MVP", "MVP Scoping", "Roadmap"])
    if not mvp_text:
        return None

    clean = _clean_markdown_line(mvp_text)
    features = []
    tech_stack = ""
    roadmap = {}

    in_features = False
    for line in clean.splitlines():
        stripped = line.strip()
        if re.search(r'\bCore\s+MVP\s+Features\b', stripped, re.IGNORECASE):
            in_features = True
            continue
        elif in_features and (stripped.startswith('#') or re.search(r'\b(?:Tech\s+Stack|Build\s+Timeline|Roadmap)\b', stripped, re.IGNORECASE)):
            in_features = False

        if in_features:
            feat_match = re.search(r'^(?:[0-9]+[.)]|\*|-)\s+(.*)', stripped)
            if feat_match:
                fname = feat_match.group(1).strip()
                if fname:
                    features.append(MVPFeature(feature_name=fname))

        if re.search(r'\bTech\s+Stack\b', stripped, re.IGNORECASE):
            t_match = re.search(r'\bTech\s+Stack\b[^\n\r:]*[:\s–—\-]+([^\n\r]+)', stripped, re.IGNORECASE)
            if t_match:
                tech_stack = t_match.group(1).strip()

        for w in range(1, 5):
            week_pattern = rf'\bWeek\s+{w}\s*\((.*?)\)'
            w_match = re.search(week_pattern, stripped, re.IGNORECASE)
            if w_match:
                roadmap[f"Week {w}"] = w_match.group(1).strip()

    if not features and not tech_stack and not roadmap:
        return None

    return MVPRecommendation(
        core_value_proposition="",
        features=features,
        tech_stack_frontend=tech_stack,
        four_week_roadmap=roadmap
    )


def _parse_gtm_strategy_from_markdown(markdown: str) -> Optional[GTMStrategy]:
    """Safely extracts GTMStrategy from Markdown report."""
    gtm_text = _extract_section_text(markdown, ["Go-To-Market", "GTM Strategy", "GTM"])
    if not gtm_text:
        return None

    clean = _clean_markdown_line(gtm_text)
    channels = []
    pricing = ""
    tactics = []

    for line in clean.splitlines():
        stripped = line.strip()
        if re.search(r'\bPricing\s+Tiers\b', stripped, re.IGNORECASE):
            p_match = re.search(r'\bPricing\s+Tiers\b[^\n\r:]*[:\s–—\-]+([^\n\r]+)', stripped, re.IGNORECASE)
            if p_match:
                pricing = p_match.group(1).strip()
        elif re.search(r'\b(?:Budget\s+Allocation|Acquisition\s+Channels)\b', stripped, re.IGNORECASE):
            c_match = re.search(r'\b(?:Budget\s+Allocation|Acquisition\s+Channels)\b[^\n\r:]*[:\s–—\-]+([^\n\r]+)', stripped, re.IGNORECASE)
            if c_match:
                channels = [c.strip(' .;') for c in re.split(r'[,;]', c_match.group(1)) if c.strip(' .;')]
        elif re.search(r'^(?:[0-9]+[.)]|\*|-)\s+(.*(?:launch|beta|seo|outreach).*)', stripped, re.IGNORECASE):
            tactics.append(stripped)

    if not channels and not pricing and not tactics:
        return None

    return GTMStrategy(
        primary_acquisition_channels=channels,
        pricing_strategy=pricing,
        launch_tactics=tactics,
        positioning_statement="",
        estimated_cac_summary=""
    )


def _extract_markdown_report(deep_result: Optional[Dict[str, Any]]) -> Optional[str]:
    """Extracts Markdown validation report strictly from /workspace/executive_validation_report.md
    or from the final AI message content blocks if the file is unavailable."""
    if not deep_result or not isinstance(deep_result, dict):
        return None

    # Priority 1: Specific executive validation report file
    files = deep_result.get("files")
    if isinstance(files, dict) and "/workspace/executive_validation_report.md" in files:
        file_entry = files["/workspace/executive_validation_report.md"]
        if isinstance(file_entry, dict) and "content" in file_entry and isinstance(file_entry["content"], str):
            content = file_entry["content"].strip()
            if content:
                return content
        elif isinstance(file_entry, str) and file_entry.strip():
            return file_entry.strip()

    # Priority 2: Final AI message content blocks containing the Markdown report
    messages = deep_result.get("messages")
    if isinstance(messages, list):
        ai_msgs = [
            m for m in messages
            if isinstance(m, AIMessage)
            or (hasattr(m, "content") and getattr(m, "type", None) == "ai")
            or (isinstance(m, dict) and m.get("role") in ("assistant", "ai"))
        ]
        for msg in reversed(ai_msgs):
            raw_content = getattr(msg, "content", None) if not isinstance(msg, dict) else msg.get("content")
            text = _extract_text_from_content(raw_content).strip()
            if text and ("#" in text or "Market" in text or "Competitor" in text or "Viability" in text):
                return text

    return None


class StartupValidatorDeepAgentsPipeline:
    """Official Deep Agents Framework Pipeline for Startup Idea Validation.

    Orchestrates the single authoritative production validation flow using the Deep Agents framework
    (create_deep_agent / self.deep_agent.invoke) with subagents and scoped context engineering.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or config.DEFAULT_MODEL

        # Specialized business agents kept ONLY for isolated unit testing & helpers
        self.planner = DeepAgentsPlanner(model_name=self.model_name)
        self.market_agent = MarketAnalysisAgent(model_name=self.model_name)
        self.competitor_agent = CompetitorAgent(model_name=self.model_name)
        self.swot_agent = SWOTRiskAgent(model_name=self.model_name)
        self.mvp_agent = MVPRecommendationAgent(model_name=self.model_name)
        self.gtm_agent = GTMStrategyAgent(model_name=self.model_name)
        self.report_agent = ReportAgent(model_name=self.model_name)
        self.tavily = TavilySearchTool()

        # 1. Define SubAgents using official Deep Agents SubAgent spec format
        self.subagents: List[SubAgent] = [
            {
                "name": "market-research",
                "description": "Researches market size (TAM, SAM, SOM), CAGR, market trends, and growth drivers.",
                "system_prompt": "You are a Market Research Subagent. Evaluate market size, CAGR, growth drivers, and target customer personas based strictly on supplied research evidence. Never invent missing figures.",
                "tools": [tavily_search_tool],
            },
            {
                "name": "competitor-research",
                "description": "Finds direct and indirect competitors, feature comparisons, pricing models, and defensibility moats.",
                "system_prompt": "You are a Competitor Research Subagent. Map the competitive landscape, direct incumbents, indirect alternatives, and defensibility moats based strictly on supplied research evidence. Never invent competitors.",
                "tools": [tavily_search_tool],
            },
            {
                "name": "swot-risk",
                "description": "Evaluates strengths, weaknesses, opportunities, threats, and severity risk matrix.",
                "system_prompt": "You are a SWOT & Risk Subagent. Formulate a SWOT analysis and severity risk matrix with mitigations grounded in available research.",
                "tools": [],
            },
            {
                "name": "mvp",
                "description": "Scopes core MVP features, technology stack, 4-week roadmap, and key metrics/KPIs.",
                "system_prompt": "You are an MVP Scoping Subagent. Define core value proposition, tech architecture, feature breakdown, and roadmap grounded in available research.",
                "tools": [],
            },
            {
                "name": "gtm",
                "description": "Formulates customer acquisition channels, positioning statement, pricing strategy, and launch tactics.",
                "system_prompt": "You are a Go-To-Market Strategy Subagent. Recommend primary acquisition channels, positioning, and launch strategy grounded in available research.",
                "tools": [],
            },
            {
                "name": "report",
                "description": "Synthesizes comprehensive validation report, overall viability index, and strategic verdict.",
                "system_prompt": "You are a Lead Executive Report Subagent. Compile all validation findings into the structured executive validation report adhering to the required markdown output contract.",
                "tools": [],
            }
        ]

        # 2. Construct Main Deep Agent graph using official deepagents API
        try:
            self.model = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=config.GEMINI_API_KEY or "not_configured"
            )
            self.deep_agent = create_deep_agent(
                model=self.model,
                subagents=self.subagents,
                system_prompt=(
                    "You are the Main Startup Validator Deep Agent orchestrating comprehensive startup idea validation. "
                    "You synthesize evidence across market-research, competitor-research, swot-risk, mvp, gtm, and report subagents. "
                    "CRITICAL GROUNDING: Base all assessments strictly on the provided web research evidence and planning context. "
                    "Never hallucinate or invent quantitative metrics (TAM/SAM/SOM/CAGR), competitor names, or pricing. "
                    "If evidence is insufficient, explicitly state 'Evidence unavailable'."
                )
            )
            logger.info("Official Deep Agents Main Validator Agent initialized successfully.")
        except Exception as e:
            logger.warning(f"Deep Agents Graph compilation warning: {e}. Pipeline operating in state mapping mode.")
            self.deep_agent = None

    def run(self, idea: StartupIdea, progress_callback: Optional[Callable[[str, str], None]] = None) -> StartupState:
        state = StartupState(idea=idea, status="initialized")

        def notify(step: str, status: str):
            if progress_callback:
                progress_callback(step, status)
            logger.info(f"Deep Agents Pipeline Step [{step}] -> {status}")

        try:
            # Step 0: Strategic Research Planning
            notify("planner", "in_progress")
            state.planning_output = self.planner.plan_validation(idea)
            notify("planner", "completed")

            # Perform live web search for market and competitor subagent intelligence
            notify("web_search", "in_progress")
            search_failed = False
            try:
                state.search_results = self.tavily.perform_validation_search(
                    idea_text=idea.idea_text,
                    industry=idea.target_industry
                )
                if not state.search_results or not (
                    getattr(state.search_results, "market_trends", None)
                    or getattr(state.search_results, "competitors", None)
                    or getattr(state.search_results, "customer_pain_points", None)
                    or getattr(state.search_results, "industry_news", None)
                    or getattr(state.search_results, "funding", None)
                ):
                    search_failed = True
            except Exception as e:
                logger.warning(f"Web search step warning: {e}")
                search_failed = True
                state.search_results = None

            if search_failed:
                notify("web_search", "failed")
                logger.warning("Web search failed or returned no results. Intelligence marked as unavailable.")
            else:
                notify("web_search", "completed")

            # SINGLE AUTHORITATIVE PRODUCTION PATH: Invoke Official Deep Agent Graph & Capture Result
            deep_result: Optional[Dict[str, Any]] = None
            if self.deep_agent:
                try:
                    logger.info("Invoking official Deep Agent Graph with subagents...")
                    search_summary = format_search_results_summary(state.search_results)
                    planning_summary = ""
                    if state.planning_output:
                        plan = state.planning_output
                        questions = "\n".join(f"- {q}" for q in plan.research_questions)
                        planning_summary = (
                            f"\nStrategic Objective: {plan.strategic_objective}\n"
                            f"Key Research Questions:\n{questions}\n"
                        )

                    prompt_content = (
                        f"Perform complete startup idea validation for idea: '{idea.idea_text}'.\n"
                        f"Target Industry: {idea.target_industry}. Target Audience: {idea.target_audience}.\n"
                        f"Business Model: {idea.business_model}. Budget: {idea.budget}. Timeline: {idea.timeline}.\n"
                        f"{planning_summary}\n"
                        f"=== WEB RESEARCH EVIDENCE SUMMARY ===\n"
                        f"{search_summary}\n"
                        f"=== END RESEARCH EVIDENCE ===\n\n"
                        f"CRITICAL GROUNDING RULES:\n"
                        f"1. Use the supplied research evidence as the primary source of truth.\n"
                        f"2. Synthesize market sizing, competitive landscape, SWOT/risk, MVP, and GTM findings strictly from the evidence.\n"
                        f"3. Never invent missing quantitative metrics (TAM, SAM, SOM, CAGR), competitor names, URLs, pricing, or defensibility moats.\n"
                        f"4. If specific evidence is unavailable or insufficient, state 'Evidence unavailable' or 'No verified competitors identified from available research.'\n\n"
                        f"OUTPUT CONTRACT:\n"
                        f"Generate the comprehensive Executive Validation Report using these exact Markdown headings and formatting:\n\n"
                        f"## 1. Market Sizing and Growth Analysis\n"
                        f"- **Total Addressable Market (TAM):** [e.g. $14.5 Billion, or Evidence unavailable]\n"
                        f"- **Serviceable Addressable Market (SAM):** [e.g. $4.0 Billion, or Evidence unavailable]\n"
                        f"- **Serviceable Obtainable Market (SOM):** [e.g. $400 Million, or Evidence unavailable]\n"
                        f"- **Projected CAGR:** [e.g. 15.2% CAGR, or Evidence unavailable]\n"
                        f"- **Growth Drivers:** [comma-separated drivers from evidence]\n"
                        f"[Market size scope summary grounded in evidence]\n\n"
                        f"## 2. Competitor Landscape and Moat\n"
                        f"- **Market Positioning:** [Positioning summary grounded in evidence]\n"
                        f"- **Defensibility Moat:** [Moat assessment grounded in evidence]\n"
                        f"### Direct Competitors:\n"
                        f"- **[Competitor Name] ([Pricing]):** [Description from evidence]\n"
                        f"### Indirect Competitors / Alternatives:\n"
                        f"- **[Alternative/Substitute]:** [Description]\n\n"
                        f"## 3. SWOT Analysis and Risk Evaluation\n"
                        f"- **Financial Risk Index:** [1-10]\n"
                        f"- **Technical Risk Index:** [1-10]\n"
                        f"- **Regulatory Risk Index:** [1-10]\n"
                        f"- **Overall Risk Score:** [1-10]\n"
                        f"- **Strengths:** [Evidence-backed strengths separated by comma]\n"
                        f"- **Weaknesses:** [Evidence-backed weaknesses separated by comma]\n"
                        f"- **Opportunities:** [Evidence-backed opportunities separated by comma]\n"
                        f"- **Threats:** [Evidence-backed threats separated by comma]\n\n"
                        f"## 4. Minimum Viable Product (MVP) Specifications\n"
                        f"- **Core Value Proposition:** [Value proposition]\n"
                        f"- **Tech Stack:** [Recommended technology stack]\n"
                        f"Core MVP Features:\n"
                        f"1. [Feature 1]: [Description]\n"
                        f"2. [Feature 2]: [Description]\n"
                        f"- **Build Timeline:**\n"
                        f"- Week 1 (Foundation): [Scope]\n"
                        f"- Week 2 (Core Logic): [Scope]\n"
                        f"- Week 3 (Integration): [Scope]\n"
                        f"- Week 4 (Launch & QA): [Scope]\n\n"
                        f"## 5. Go-To-Market (GTM) Strategy\n"
                        f"- **Positioning Statement:** [Positioning statement]\n"
                        f"- **Pricing Tiers:** [Pricing structure]\n"
                        f"- **Acquisition Channels:** [Primary channels separated by comma]\n"
                        f"- **Launch Tactics:**\n"
                        f"1. [Tactic 1]\n"
                        f"2. [Tactic 2]\n\n"
                        f"Produce the full report directly in your final response. If write_file is available, also write this report to /workspace/executive_validation_report.md."
                    )
                    graph_input = {"messages": [{"role": "user", "content": prompt_content}]}
                    deep_result = self.deep_agent.invoke(graph_input)
                    logger.info("Official Deep Agent graph invoked and executed successfully.")
                except Exception as ge:
                    logger.warning(f"Deep Agent graph execution note: {ge}. Using state mapping.")

            # Store the raw deep_result on state for downstream integration verification
            state.deep_result = deep_result

            # Parse and map deep_result output into structured Pydantic models
            self._map_deep_result_to_state(state, deep_result, notify)

            state.status = "completed"
            return state

        except Exception as e:
            logger.exception(f"Deep Agents Pipeline execution failed: {e}")
            state.status = "error"
            state.error = str(e)
            return state

    def _map_deep_result_to_state(
        self,
        state: StartupState,
        deep_result: Optional[Dict[str, Any]],
        notify: Callable[[str, str], None]
    ) -> None:
        """Maps output from deep_result into StartupState Pydantic models.

        Priority 1: Structured JSON (deep_result["structured_response"] or AI message JSON).
        Priority 2: Markdown report (from /workspace/executive_validation_report.md or final AI message).
        Fallback: Honest unavailable indicators without fabricating data.
        """
        parsed_json: Optional[Dict[str, Any]] = None

        if deep_result:
            # Priority 1A: Check structured response first
            if isinstance(deep_result.get("structured_response"), dict):
                parsed_json = deep_result["structured_response"]
            # Priority 1B: Extract JSON payload from AIMessage history
            elif "messages" in deep_result:
                ai_msgs = [
                    m for m in deep_result["messages"]
                    if isinstance(m, AIMessage)
                    or (hasattr(m, "content") and getattr(m, "type", None) == "ai")
                    or (isinstance(m, dict) and m.get("role") in ("assistant", "ai"))
                ]
                for msg in reversed(ai_msgs):
                    raw_content = getattr(msg, "content", None) if not isinstance(msg, dict) else msg.get("content")
                    text_content = _extract_text_from_content(raw_content)
                    if "{" in text_content and "}" in text_content:
                        try:
                            start_idx = text_content.index("{")
                            end_idx = text_content.rindex("}") + 1
                            loaded = json.loads(text_content[start_idx:end_idx])
                            if isinstance(loaded, dict):
                                parsed_json = loaded
                                break
                        except Exception:
                            continue

        # Priority 2: Extract from Markdown report if structured JSON is not available
        markdown_report: Optional[str] = None
        if not parsed_json and deep_result:
            markdown_report = _extract_markdown_report(deep_result)

        # 1. Market Analysis Mapping
        notify("market_analysis", "in_progress")
        if parsed_json and "market_analysis" in parsed_json:
            try:
                state.market_analysis = MarketAnalysis.model_validate(parsed_json["market_analysis"])
            except Exception as me:
                logger.warning(f"MarketAnalysis schema validation error: {me}")
        elif markdown_report:
            state.market_analysis = _parse_market_analysis_from_markdown(markdown_report)

        if not state.market_analysis:
            state.market_analysis = MarketAnalysis(
                tam_billions=None,
                sam_billions=None,
                som_billions=None,
                market_size_summary="Market size could not be established from available research.",
                cagr_percentage=None,
                key_growth_drivers=[],
                target_personas=[],
                market_readiness_score=None
            )
        notify("market_analysis", "completed")

        # 2. Competitor Analysis Mapping
        notify("competitor_analysis", "in_progress")
        if parsed_json and "competitor_analysis" in parsed_json:
            try:
                state.competitor_analysis = CompetitorAnalysis.model_validate(parsed_json["competitor_analysis"])
            except Exception as ce:
                logger.warning(f"CompetitorAnalysis schema validation error: {ce}")
        elif markdown_report:
            state.competitor_analysis = _parse_competitor_analysis_from_markdown(markdown_report)

        if not state.competitor_analysis:
            state.competitor_analysis = CompetitorAnalysis(
                direct_competitors=[],
                indirect_competitors=[],
                feature_comparison_matrix={},
                market_positioning_summary="No verified competitors identified from available research.",
                moat_assessment="Defensibility cannot be evaluated without verified competitor evidence."
            )
        notify("competitor_analysis", "completed")

        # 3. SWOT & Risk Mapping
        notify("swot_risk", "in_progress")
        if parsed_json and "swot_analysis" in parsed_json:
            try:
                state.swot_analysis = SWOTAnalysis.model_validate(parsed_json["swot_analysis"])
            except Exception as se:
                logger.warning(f"SWOTAnalysis schema validation error: {se}")
                state.swot_analysis = None
        elif markdown_report:
            state.swot_analysis = _parse_swot_analysis_from_markdown(markdown_report)
        else:
            state.swot_analysis = None
        notify("swot_risk", "completed" if state.swot_analysis else "unavailable")

        # 4. MVP Recommendation Mapping
        notify("mvp_recommendation", "in_progress")
        if parsed_json and "mvp_recommendation" in parsed_json:
            try:
                state.mvp_recommendation = MVPRecommendation.model_validate(parsed_json["mvp_recommendation"])
            except Exception as me:
                logger.warning(f"MVPRecommendation schema validation error: {me}")
                state.mvp_recommendation = None
        elif markdown_report:
            state.mvp_recommendation = _parse_mvp_recommendation_from_markdown(markdown_report)
        else:
            state.mvp_recommendation = None
        notify("mvp_recommendation", "completed" if state.mvp_recommendation else "unavailable")

        # 5. GTM Strategy Mapping
        notify("gtm_strategy", "in_progress")
        if parsed_json and "gtm_strategy" in parsed_json:
            try:
                state.gtm_strategy = GTMStrategy.model_validate(parsed_json["gtm_strategy"])
            except Exception as ge:
                logger.warning(f"GTMStrategy schema validation error: {ge}")
                state.gtm_strategy = None
        elif markdown_report:
            state.gtm_strategy = _parse_gtm_strategy_from_markdown(markdown_report)
        else:
            state.gtm_strategy = None
        notify("gtm_strategy", "completed" if state.gtm_strategy else "unavailable")

        # 6. Final Executive Report Synthesis & Deterministic Scoring Engine
        notify("report", "in_progress")
        # Determine verified competitor count vs missing evidence
        comp_count = None
        moat_val = "Medium"
        if state.competitor_analysis:
            moat_val = state.competitor_analysis.moat_assessment or "Medium"
            if state.competitor_analysis.direct_competitors:
                comp_count = len(state.competitor_analysis.direct_competitors)
            elif "No verified competitors" not in (state.competitor_analysis.market_positioning_summary or ""):
                comp_count = 0
            else:
                comp_count = None

        fin_risk = state.swot_analysis.financial_risk if state.swot_analysis else 5
        tech_risk = state.swot_analysis.technical_risk if state.swot_analysis else 5
        reg_risk = state.swot_analysis.regulatory_risk if state.swot_analysis else 4

        scoring_breakdown = DeterministicScoringEngine.calculate_scores(
            idea_text=state.idea.idea_text,
            target_industry=state.idea.target_industry or "Technology / SaaS",
            tam_billions=state.market_analysis.tam_billions if state.market_analysis else None,
            sam_billions=state.market_analysis.sam_billions if state.market_analysis else None,
            som_billions=state.market_analysis.som_billions if state.market_analysis else None,
            cagr_percentage=state.market_analysis.cagr_percentage if state.market_analysis else None,
            direct_competitor_count=comp_count,
            moat_level=moat_val,
            financial_risk=fin_risk,
            technical_risk=tech_risk,
            regulatory_risk=reg_risk,
            has_web_research=bool(state.search_results),
            has_swot=state.swot_analysis is not None,
            has_mvp=state.mvp_recommendation is not None,
            has_gtm=state.gtm_strategy is not None
        )

        if not state.swot_analysis:
            scoring_breakdown.evidence_limitations.append("SWOT and risk analysis could not be verified from available research.")

        if not state.search_results:
            scoring_breakdown.evidence_limitations.append("Live web research was unavailable; market and competitor intelligence could not be verified in real time.")

        if state.market_analysis and state.market_analysis.tam_billions is not None:
            if state.market_analysis.cagr_percentage is not None:
                tam_takeaway = f"Target Market TAM of ${state.market_analysis.tam_billions}B with projected CAGR of {state.market_analysis.cagr_percentage}%."
            else:
                tam_takeaway = f"Target Market TAM of ${state.market_analysis.tam_billions}B."
        else:
            tam_takeaway = "Target Market sizing could not be established from available research."

        state.final_report = ValidationReport(
            overall_viability_score=scoring_breakdown.total_viability_score,
            verdict=scoring_breakdown.verdict,
            executive_summary=f"Executive Strategic Evaluation for '{state.idea.idea_text}' ({state.idea.target_industry}). Overall Viability Index is {scoring_breakdown.total_viability_score}/100 with a strategic verdict of {scoring_breakdown.verdict}.",
            scoring_breakdown=scoring_breakdown,
            market_score=int((scoring_breakdown.market_opportunity_score / 20.0) * 100),
            competitor_score=int((scoring_breakdown.competition_score / 15.0) * 100),
            risk_score=int((scoring_breakdown.execution_risk_score / 10.0) * 100),
            mvp_score=int((scoring_breakdown.technical_feasibility_score / 10.0) * 100),
            gtm_score=int((scoring_breakdown.scalability_score / 15.0) * 100),
            investor_readiness_score=scoring_breakdown.investor_readiness_score,
            funding_probability=scoring_breakdown.funding_probability,
            pmf_score=scoring_breakdown.pmf_score,
            confidence_score=scoring_breakdown.overall_confidence_score,
            key_takeaways=[
                f"Deterministically scored overall viability index of {scoring_breakdown.total_viability_score}/100 based on an 8-dimension weighted matrix.",
                tam_takeaway,
                f"Strategic verdict classified as '{scoring_breakdown.verdict}'."
            ],
            recommended_next_steps=[
                "Build 4-week MVP focused on core automated workflow",
                "Conduct 15 customer discovery interviews",
                "Establish initial landing page for conversion validation"
            ]
        )
        notify("report", "completed")
