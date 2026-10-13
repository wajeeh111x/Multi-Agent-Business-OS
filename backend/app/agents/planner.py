import json

from app.ai.ollama_client import ask_llm
from app.agents.tool_definitions import TOOLS


# ============================================================
# SIMPLE ROUTING
# ============================================================

def simple_route(message: str):

    text = message.lower().strip()

    # --------------------------------------------------------
    # Greetings / small talk
    # --------------------------------------------------------

    greetings = [
        "hello",
        "hi",
        "hey",
        "hello there",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "thanks",
        "thank you",
        "bye",
        "goodbye"
    ]

    if text in greetings:

        return [
            {
                "tool": "chat",
                "arguments": {}
            }
        ]

    # --------------------------------------------------------
    # List documents
    # --------------------------------------------------------

    list_phrases = [
        "list my documents",
        "list documents",
        "show my documents",
        "show documents",
        "what documents do i have",
        "which documents do i have",
        "uploaded documents",
        "my uploaded files"
    ]

    if any(phrase in text for phrase in list_phrases):

        return [
            {
                "tool": "list_documents",
                "arguments": {}
            }
        ]

    # --------------------------------------------------------
    # Delete document
    # --------------------------------------------------------

    delete_words = [
        "delete ",
        "remove ",
        "erase "
    ]

    for word in delete_words:

        if text.startswith(word):

            filename = message[len(word):].strip()

            if filename:

                return [
                    {
                        "tool": "delete_document",
                        "arguments": {
                            "filename": filename
                        }
                    }
                ]

    return None


# ============================================================
# LLM PLANNER
# ============================================================

def llm_plan(message: str, history: str):

    prompt = f"""
You are the planning system for Business OS AI.

Conversation History:
{history}

Current User Message:
{message}

Available tools:
{json.dumps(TOOLS, indent=2)}

Your job is to decide which tool or tools are actually
required.

IMPORTANT ROUTING RULES:

1. Greetings and casual conversation do NOT require
   document search or web search.

2. Questions about uploaded PDFs require:
   search_documents

3. Requests to list uploaded files require:
   list_documents

4. Requests to delete a document require:
   delete_document

5. Questions asking for current, latest, recent, today's,
   live, or internet information require:
   web_search

6. Business datasets such as CSV or Excel files should use
   the data analysis tools.

7. Requests about understanding or analyzing a dataset
   should use:
   dataset_summary
   preview_dataset
   numeric_summary

8. If the user asks for general business data analysis,
   choose the most appropriate data tool.

9. If the user asks a general question that does not require
   documents, web search, or business data analysis, use:

   {{
       "tool": "chat",
       "arguments": {{}}
   }}

10. If multiple tools are genuinely required, return
    multiple steps.

11. Do not use tools just because they are available.

12. Return ONLY a JSON array.

Examples:

User:
Hello

Response:
[
    {{
        "tool": "chat",
        "arguments": {{}}
    }}
]

User:
What documents do I have?

Response:
[
    {{
        "tool": "list_documents",
        "arguments": {{}}
    }}
]

User:
Summarize my PDF

Response:
[
    {{
        "tool": "search_documents",
        "arguments": {{
            "question": "Summarize my PDF"
        }}
    }}
]

User:
What is the latest AI news?

Response:
[
    {{
        "tool": "web_search",
        "arguments": {{
            "query": "latest AI news"
        }}
    }}
]

User:
What is artificial intelligence?

Response:
[
    {{
        "tool": "chat",
        "arguments": {{}}
    }}
]

User:
Analyze my sales CSV

Response:
[
    {{
        "tool": "dataset_summary",
        "arguments": {{
            "filepath": "PATH_TO_FILE"
        }}
    }}
]

User:
Show me the first rows of my sales file

Response:
[
    {{
        "tool": "preview_dataset",
        "arguments": {{
            "filepath": "PATH_TO_FILE",
            "rows": 5
        }}
    }}
]

User:
Give me statistics from my sales dataset

Response:
[
    {{
        "tool": "numeric_summary",
        "arguments": {{
            "filepath": "PATH_TO_FILE"
        }}
    }}
]

User:
Search my documents for the company policy and
compare it with the latest AI regulations.

Response:
[
    {{
        "tool": "search_documents",
        "arguments": {{
            "question": "company policy"
        }}
    }},
    {{
        "tool": "web_search",
        "arguments": {{
            "query": "latest AI regulations"
        }}
    }}
]

IMPORTANT:

Return ONLY JSON.
Do NOT use markdown.
Do NOT use ```json.
Do NOT explain anything.

The response MUST begin with [
The response MUST end with ]
"""

    response = ask_llm(prompt)

    print("=" * 80)
    print("LLM PLANNER OUTPUT:")
    print(response)
    print("=" * 80)

    response = response.strip()

    # --------------------------------------------------------
    # Remove markdown fences
    # --------------------------------------------------------

    if response.startswith("```json"):

        response = response[7:]

    elif response.startswith("```"):

        response = response[3:]

    if response.endswith("```"):

        response = response[:-3]

    response = response.strip()

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        plan = json.loads(response)

        if not isinstance(plan, list):

            raise ValueError(
                "Planner response is not a list."
            )

        # ----------------------------------------------------
        # Validate tools
        # ----------------------------------------------------

        valid_tools = {
            "chat",

            # Document tools
            "search_documents",
            "list_documents",
            "delete_document",

            # Web tools
            "web_search",

            # Business Intelligence tools
            "dataset_summary",
            "preview_dataset",
            "numeric_summary"
        }

        clean_plan = []

        for step in plan:

            if not isinstance(step, dict):
                continue

            tool = step.get("tool")

            if tool not in valid_tools:
                continue

            arguments = step.get(
                "arguments",
                {}
            )

            if not isinstance(arguments, dict):

                arguments = {}

            clean_plan.append(
                {
                    "tool": tool,
                    "arguments": arguments
                }
            )

        if clean_plan:

            return clean_plan

    except Exception as e:

        print(
            "Planner JSON Error:",
            e
        )

    # --------------------------------------------------------
    # Safe fallback
    # --------------------------------------------------------

    return [
        {
            "tool": "chat",
            "arguments": {}
        }
    ]


# ============================================================
# MAIN PLANNER
# ============================================================

def create_plan(
    message: str,
    history: str = ""
):

    # --------------------------------------------------------
    # First try deterministic routing
    # --------------------------------------------------------

    route = simple_route(message)

    if route is not None:

        print("=" * 80)
        print("SIMPLE ROUTER:")
        print(route)
        print("=" * 80)

        return route

    # --------------------------------------------------------
    # Otherwise use LLM planner
    # --------------------------------------------------------

    return llm_plan(
        message=message,
        history=history
    )