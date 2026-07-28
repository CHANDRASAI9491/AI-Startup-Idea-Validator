from agents.web_search_agent import WebSearchAgent
from state.schema import StartupIdea

agent = WebSearchAgent()

idea = StartupIdea(idea_text="AI Startup Validator")
results = agent.run(idea)

for category, items in results.model_dump().items():
    print("\n" + "=" * 60)
    print(category.upper())
    print("=" * 60)

    for item in items:
        print(item["title"])
        print(item["url"])
        print(item["snippet"])
        print()