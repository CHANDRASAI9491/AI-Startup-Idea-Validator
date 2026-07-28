from tools.duckduckgo_tool import DuckDuckGoTool


class WebSearchAgent:

    def __init__(self):

        self.search_tool = DuckDuckGoTool()

    def run(self, startup_idea: str):

        queries = {

            "market_trends":
                f"{startup_idea} market trends",

            "competitors":
                f"{startup_idea} competitors",

            "customer_pain_points":
                f"{startup_idea} customer pain points",

            "industry_news":
                f"{startup_idea} latest news",

            "funding":
                f"{startup_idea} startup funding"
        }

        output = {}

        for category, query in queries.items():

            print(f"\nSearching: {category}")

            output[category] = self.search_tool.search(
                query,
                max_results=5
            )

        return output