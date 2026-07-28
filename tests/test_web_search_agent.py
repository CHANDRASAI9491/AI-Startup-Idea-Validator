from agents.web_search_agent import WebSearchAgent


agent = WebSearchAgent()

results = agent.run(
    "AI Startup Validator"
)

for category, items in results.items():

    print("\n")
    print("=" * 60)
    print(category.upper())
    print("=" * 60)

    for item in items:

        print(item["title"])
        print(item["url"])
        print(item["snippet"])
        print()