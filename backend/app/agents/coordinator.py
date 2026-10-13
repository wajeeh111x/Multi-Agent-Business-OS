from app.agents.document_agent import document_agent
from app.agents.web_agent import web_agent
from app.agents.chat_agent import chat_agent
from app.agents.data_agent import data_agent


DOCUMENT_TOOLS = {
    "search_documents",
    "list_documents",
    "delete_document"
}


WEB_TOOLS = {
    "web_search"
}


DATA_TOOLS = {
    "dataset_summary",
    "preview_dataset",
    "numeric_summary"
}


def execute_step(
    step,
    message,
    history=""
):

    tool = step.get("tool")

    arguments = step.get(
        "arguments",
        {}
    )

    # Document Agent
    if tool in DOCUMENT_TOOLS:

        return document_agent(
            tool,
            arguments
        )

    # Web Agent
    if tool in WEB_TOOLS:

        return web_agent(
            arguments
        )

    # Data Agent
    if tool in DATA_TOOLS:

        return data_agent(
            tool,
            arguments
        )

    # General Chat Agent
    return chat_agent(
        message,
        history
    )