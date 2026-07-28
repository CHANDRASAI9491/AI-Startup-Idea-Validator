from tools.duckduckgo_tool import DuckDuckGoTool

tool = DuckDuckGoTool()

results = tool.search(
    "AI Startup Validator market trends",
    max_results=5
)

for index, item in enumerate(results):

    print()

    print("=" * 60)

    print("Result", index + 1)

    print("=" * 60)

    print("Title :", item["title"])

    print("URL   :", item["url"])

    print("Snippet :", item["snippet"])