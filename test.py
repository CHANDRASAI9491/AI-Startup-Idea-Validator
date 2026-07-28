from ddgs import DDGS

with DDGS() as ddgs:
    results = ddgs.text(
        "AI Startup Validator",
        max_results=3
    )

    for result in results:
        print(result)