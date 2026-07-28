from typing import Dict, Any, List
from tools.duckduckgo_tool import DuckDuckGoTool
from state.schema import SearchResultItem, WebSearchResults


class WebSearchTool:

    def __init__(self):
        self.ddg = DuckDuckGoTool()

    def run_multi_query_search(self, startup_idea: str, max_results: int = 5) -> WebSearchResults:
        categories = {
            "market_trends": f"{startup_idea} market trends growth report",
            "competitors": f"{startup_idea} main competitors alternatives startups",
            "customer_pain_points": f"{startup_idea} customer pain points challenges reviews",
            "industry_news": f"{startup_idea} industry news analysis",
            "funding": f"{startup_idea} startup funding venture capital investments"
        }

        results_dict: Dict[str, List[SearchResultItem]] = {}

        for category, query in categories.items():
            raw_items = self.ddg.search(query, max_results=max_results)
            parsed_items = [
                SearchResultItem(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", "")
                )
                for item in raw_items
            ]
            results_dict[category] = parsed_items

        return WebSearchResults(
            market_trends=results_dict.get("market_trends", []),
            competitors=results_dict.get("competitors", []),
            customer_pain_points=results_dict.get("customer_pain_points", []),
            industry_news=results_dict.get("industry_news", []),
            funding=results_dict.get("funding", [])
        )
