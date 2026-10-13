TOOLS = [

    {
        "name": "search_documents",
        "description": (
            "Search uploaded PDF documents and answer questions "
            "using their contents."
        ),
        "parameters": {
            "question": "string"
        }
    },

    {
        "name": "list_documents",
        "description": (
            "List all uploaded PDF documents."
        ),
        "parameters": {}
    },

    {
        "name": "delete_document",
        "description": (
            "Delete an uploaded PDF document."
        ),
        "parameters": {
            "filename": "string"
        }
    },

    {
        "name": "web_search",
        "description": (
            "Search the internet for current or up-to-date "
            "information."
        ),
        "parameters": {
            "query": "string"
        }
    }
]

