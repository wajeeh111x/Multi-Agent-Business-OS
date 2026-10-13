from app.agents.document_agent import document_agent
from app.agents.chat_agent import chat_agent
from app.agents.research_agent import research_agent


def supervisor(plan, message, history):

    outputs = []

    for step in plan:

        tool = step["tool"]
        args = step.get("arguments", {})

        if tool in [
            "search_documents",
            "list_documents",
            "delete_document"
        ]:
            result = document_agent(tool, args)

        elif tool == "web_search":
            result = research_agent(tool, args)

        else:
            result = chat_agent(message, history)

        outputs.append(result)

    return outputs