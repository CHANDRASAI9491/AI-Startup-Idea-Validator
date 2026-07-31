import re
import json
import logging
from typing import List, Dict, Any, Optional
from state.schema import SearchResultItem, WebSearchResults

logger = logging.getLogger(__name__)


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extracts and parses JSON object or array from LLM response text."""
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            pass

    return None


def format_search_results_summary(results: Optional[WebSearchResults], max_items: int = 5) -> str:
    """Formats WebSearchResults into a clean text summary for agent prompts."""
    if not results:
        return "No web search results available."

    lines = []
    if results.market_trends:
        lines.append("Market Trends & Industry Insights:")
        for item in results.market_trends[:max_items]:
            lines.append(f"- {item.title}: {item.snippet}")

    if results.competitors:
        lines.append("\nCompetitor Information:")
        for item in results.competitors[:max_items]:
            lines.append(f"- {item.title}: {item.snippet}")

    if results.customer_pain_points:
        lines.append("\nCustomer Pain Points & Feedback:")
        for item in results.customer_pain_points[:max_items]:
            lines.append(f"- {item.title}: {item.snippet}")

    return "\n".join(lines) if lines else "No relevant search snippets found."


class RetrievalUtils:
    """Helper utilities for web search snippet deduplication, relevance scoring, and query formatting."""

    @staticmethod
    def deduplicate_results(results: List[SearchResultItem]) -> List[SearchResultItem]:
        seen_urls = set()
        unique = []
        for item in results:
            if item.url not in seen_urls and len(item.snippet) > 20:
                seen_urls.add(item.url)
                unique.append(item)
        return unique

    @staticmethod
    def rank_snippets(results: List[SearchResultItem], keywords: List[str]) -> List[SearchResultItem]:
        def score(item: SearchResultItem) -> int:
            text = (item.title + " " + item.snippet).lower()
            return sum(1 for kw in keywords if kw.lower() in text)

        return sorted(results, key=score, reverse=True)

    @staticmethod
    def format_search_summary(results: List[SearchResultItem], max_items: int = 5) -> str:
        summary_lines = []
        for i, item in enumerate(results[:max_items], 1):
            summary_lines.append(f"{i}. [{item.title}]({item.url}): {item.snippet}")
        return "\n".join(summary_lines)
