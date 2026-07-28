import re
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extracts JSON object from a string that might contain markdown backticks or conversational wrapper text."""
    if not text:
        return None

    # Try direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Regex search for ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Search for first { to last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return None


def format_search_results_summary(search_results: Any) -> str:
    """Formats WebSearchResults into a structured markdown text string for LLM prompting."""
    if not search_results:
        return "No web search data available."

    sections = []
    
    dict_data = search_results.model_dump() if hasattr(search_results, "model_dump") else search_results
    
    for category, items in dict_data.items():
        sections.append(f"### Category: {category.upper().replace('_', ' ')}")
        if isinstance(items, list):
            for i, item in enumerate(items, 1):
                title = item.get("title", "")
                url = item.get("url", "")
                snippet = item.get("snippet", "")
                sections.append(f"{i}. [{title}]({url})\n   Snippet: {snippet}")
        sections.append("")

    return "\n".join(sections)
