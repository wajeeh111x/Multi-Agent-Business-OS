from app.agents.tools import (
    search_documents,
    list_documents,
    delete_document
)


def document_agent(tool: str, arguments: dict):

    try:

        if tool == "search_documents":
            return search_documents(**arguments)

        if tool == "list_documents":
            return list_documents()

        if tool == "delete_document":
            return delete_document(**arguments)

        return {
            "answer": f"Unknown document tool: {tool}",
            "sources": []
        }

    except Exception as e:

        return {
            "answer": f"Document Agent Error: {str(e)}",
            "sources": []
        }