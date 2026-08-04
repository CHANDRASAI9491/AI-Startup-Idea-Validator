from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv("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"))

def tavily_search(query):
    return client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )