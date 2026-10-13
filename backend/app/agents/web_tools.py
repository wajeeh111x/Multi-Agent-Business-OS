from duckduckgo_search import DDGS


def web_search(query: str):

    results = []

    with DDGS() as ddgs:
        search_results = ddgs.text(
            query,
            max_results=5
        )

        for item in search_results:
            results.append({
                "title": item.get("title", ""),
                "body": item.get("body", ""),
                "url": item.get("href", "")
            })

    context = ""

    sources = []

    for item in results:
        context += f"""
Title: {item['title']}
Content: {item['body']}
URL: {item['url']}

"""

        sources.append(item["url"])

    return {
        "answer": context,
        "sources": sources
    }