from tools.web_search_tool import WebSearchTool
from state.schema import WebSearchResults, StartupIdea


class WebSearchAgent:

    def __init__(self):
        self.search_tool = WebSearchTool()

    def run(self, startup_idea: StartupIdea, max_results: int = 5) -> WebSearchResults:
        idea_text = startup_idea.idea_text if hasattr(startup_idea, "idea_text") else str(startup_idea)
        return self.search_tool.run_multi_query_search(idea_text, max_results=max_results)