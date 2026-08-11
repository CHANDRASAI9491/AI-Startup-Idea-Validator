from agents.web_search_agent import WebSearchAgent
from state.schema import StartupIdea, StartupState


def test_web_search_agent():
    idea = StartupIdea(
        idea_text="AI-powered healthcare assistant for hospitals",
        target_industry="Healthcare"
    )

    state = StartupState(idea=idea)

    agent = WebSearchAgent()

    result = agent.execute(state)

    assert result.error is None

    assert result.search_results is not None

    print("\n===== WEB SEARCH RESULTS =====")
    print(result.search_results)


if __name__ == "__main__":
    test_web_search_agent()