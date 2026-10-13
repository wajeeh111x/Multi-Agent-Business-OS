from app.agents.tools import web_search


def web_agent(arguments: dict):
    """
    Web Agent

    Executes internet searches safely and returns
    a consistent response structure.
    """

    try:

        if not isinstance(arguments, dict):
            return {
                "answer": "Invalid web search arguments.",
                "sources": []
            }

        query = arguments.get("query", "").strip()

        if not query:
            return {
                "answer": "Please provide a search query.",
                "sources": []
            }

        result = web_search(query=query)

        if not isinstance(result, dict):
            return {
                "answer": str(result),
                "sources": []
            }

        return {
            "answer": result.get(
                "answer",
                "No web results found."
            ),
            "sources": result.get(
                "sources",
                []
            )
        }

    except Exception as e:

        print("Web Agent Error:", e)

        return {
            "answer": f"Web search failed: {str(e)}",
            "sources": []
        }