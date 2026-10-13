import os
import chromadb

from app.rag.retriever import retrieve
from app.rag.prompt import build_prompt
from app.ai.ollama_client import ask_llm
from duckduckgo_search import DDGS


# =========================================================
# CHROMA DATABASE
# =========================================================

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="documents"
)


# =========================================================
# SEARCH DOCUMENTS
# =========================================================

def search_documents(question: str):

    try:

        retrieved = retrieve(question)

        documents = retrieved.get("documents", [])
        metadatas = retrieved.get("metadatas", [])

        if (
            not documents
            or not documents[0]
        ):
            return {
                "answer": "No document found.",
                "sources": []
            }

        prompt = build_prompt(
            question,
            retrieved
        )

        answer = ask_llm(prompt)

        sources = []

        if metadatas and metadatas[0]:

            for metadata in metadatas[0]:

                if isinstance(metadata, dict):

                    sources.append({
                        "type": "document",
                        "source": metadata.get(
                            "source",
                            ""
                        ),
                        "page": metadata.get(
                            "page"
                        )
                    })

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:

        return {
            "answer": f"Document search failed: {str(e)}",
            "sources": []
        }


# =========================================================
# LIST DOCUMENTS
# =========================================================

def list_documents():

    try:

        data = collection.get()

        metadatas = data.get(
            "metadatas",
            []
        )

        if not metadatas:

            return {
                "answer": "No uploaded documents.",
                "sources": []
            }

        filenames = []

        for meta in metadatas:

            if not isinstance(meta, dict):
                continue

            filename = meta.get(
                "source"
            )

            if (
                filename
                and filename not in filenames
            ):

                filenames.append(
                    filename
                )

        if not filenames:

            return {
                "answer": "No uploaded documents.",
                "sources": []
            }

        return {
            "answer": "\n".join(filenames),
            "sources": []
        }

    except Exception as e:

        return {
            "answer": f"Could not list documents: {str(e)}",
            "sources": []
        }


# =========================================================
# DELETE DOCUMENT
# =========================================================

def delete_document(filename: str):

    try:

        filepath = os.path.join(
            "uploads",
            filename
        )

        deleted_file = False

        # -------------------------------------------------
        # Delete physical file
        # -------------------------------------------------

        if os.path.exists(filepath):

            os.remove(filepath)

            deleted_file = True

        # -------------------------------------------------
        # Delete Chroma records
        # -------------------------------------------------

        data = collection.get()

        ids = data.get(
            "ids",
            []
        )

        delete_ids = []

        for doc_id in ids:

            if isinstance(doc_id, str):

                if doc_id.startswith(filename):

                    delete_ids.append(
                        doc_id
                    )

        if delete_ids:

            collection.delete(
                ids=delete_ids
            )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        if deleted_file or delete_ids:

            answer = (
                f"{filename} deleted successfully."
            )

        else:

            answer = (
                f"{filename} was not found."
            )

        return {
            "answer": answer,
            "sources": []
        }

    except Exception as e:

        return {
            "answer": f"Delete failed: {str(e)}",
            "sources": []
        }


# =========================================================
# WEB SEARCH
# =========================================================

def web_search(query: str):

    results = []

    try:

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                max_results=5
            )

            for item in search_results:

                if not isinstance(item, dict):
                    continue

                results.append({
                    "title": item.get(
                        "title",
                        ""
                    ),
                    "body": item.get(
                        "body",
                        ""
                    ),
                    "url": item.get(
                        "href",
                        ""
                    )
                })

    except Exception as e:

        return {
            "answer": f"Web search failed: {str(e)}",
            "sources": []
        }

    # -----------------------------------------------------
    # No results
    # -----------------------------------------------------

    if not results:

        return {
            "answer": "No web results found.",
            "sources": []
        }

    # -----------------------------------------------------
    # Build context
    # -----------------------------------------------------

    context_parts = []

    sources = []

    for result in results:

        title = result.get(
            "title",
            ""
        )

        body = result.get(
            "body",
            ""
        )

        url = result.get(
            "url",
            ""
        )

        context_parts.append(
            f"""
Title:
{title}

Content:
{body}

URL:
{url}
"""
        )

        # IMPORTANT:
        # sources must ALWAYS contain dictionaries.

        if url:

            sources.append({
                "type": "web",
                "title": title,
                "url": url
            })

    context = "\n".join(
        context_parts
    )

    return {
        "answer": context,
        "sources": sources
    }


# =========================================================
# TOOL REGISTRY
# =========================================================

TOOLS_MAP = {

    "search_documents":
        search_documents,

    "list_documents":
        list_documents,

    "delete_document":
        delete_document,

    "web_search":
        web_search,

}