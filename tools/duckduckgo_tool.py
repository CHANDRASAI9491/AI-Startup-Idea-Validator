from ddgs import DDGS


class DuckDuckGoTool:

    def search(self, query: str, max_results: int = 5):

        results = []

        with DDGS() as ddgs:

            response = ddgs.text(query, max_results=max_results)

            for item in response:

                results.append({
                    "title": item.get("title"),
                    "url": item.get("href"),
                    "snippet": item.get("body")
                })

        return results