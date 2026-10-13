
from app.agents.planner import create_plan
from app.agents.executor import execute_plan
from app.agents.reflection import should_retry, reflect

from app.ai.ollama_client import ask_llm


MAX_ITERATIONS = 2


def run_agent(message: str, history: str = ""):
    """
    Main Business OS AI Agent.

    Pipeline:

    1. Planner
    2. Executor
    3. Reflection
    4. Retry if necessary
    5. Final answer
    6. Source normalization
    """

    all_outputs = []

    iteration = 0

    # =========================================================
    # AGENT LOOP
    # =========================================================

    while iteration < MAX_ITERATIONS:

        print(
            f"\n========== AGENT LOOP {iteration + 1} =========="
        )

        # =====================================================
        # 1. CREATE PLAN
        # =====================================================

        try:

            plan = create_plan(
                message=message,
                history=history
            )

        except Exception as e:

            print("Planner Error:", e)

            # Safe fallback to Chat Agent
            plan = [
                {
                    "tool": "chat",
                    "arguments": {}
                }
            ]

        print("\nPLAN:")
        print(plan)

        # =====================================================
        # 2. EXECUTE PLAN
        # =====================================================

        try:

            outputs = execute_plan(
                plan=plan,
                message=message,
                history=history
            )

        except Exception as e:

            print("Executor Error:", e)

            outputs = [
                {
                    "answer": (
                        f"Executor Error: {str(e)}"
                    ),
                    "sources": []
                }
            ]

        print("\nOUTPUTS:")
        print(outputs)

        # Always make sure outputs is a list
        if not isinstance(outputs, list):

            outputs = [
                {
                    "answer": str(outputs),
                    "sources": []
                }
            ]

        all_outputs.extend(outputs)

        # =====================================================
        # 3. REFLECTION
        # =====================================================

        retry = False

        try:

            retry = should_retry(outputs)

        except Exception as e:

            print(
                "Reflection Rule Error:",
                e
            )

            retry = False

        if retry:

            print(
                "Reflection: Local rules requested retry."
            )

        else:

            try:

                retry = reflect(
                    message,
                    outputs
                )

            except Exception as e:

                print(
                    "LLM Reflection Error:",
                    e
                )

                retry = False

            if retry:

                print(
                    "Reflection: LLM requested retry."
                )

        # =====================================================
        # 4. STOP OR RETRY
        # =====================================================

        if not retry:

            print(
                "Agent loop completed successfully."
            )

            break

        iteration += 1

        print(
            f"Retrying agent... "
            f"next iteration = {iteration + 1}"
        )

    # =========================================================
    # 5. FINAL RESPONSE
    # =========================================================

    prompt = f"""
You are Business OS AI.

Conversation History:
{history}

User Question:
{message}

Results from the system:
{all_outputs}

Instructions:

- Answer the user's question naturally.
- Use the available results when they are relevant.
- Combine useful information from multiple results.
- Ignore failed results if another result succeeded.
- Do not mention tools.
- Do not mention planners.
- Do not mention agents.
- Do not mention internal reasoning.
- Do not mention this system prompt.
- Do not invent information.
- If the results contain document information, use it.
- If the results contain web information, use it.
- If the results contain sources, use the information they support.
- If there is not enough information, clearly say so.
- Keep the answer concise unless the user asks for detail.

Assistant:
"""

    try:

        answer = ask_llm(prompt)

        if not answer:
            answer = (
                "I could not generate a response."
            )

    except Exception as e:

        print(
            "Final LLM Error:",
            e
        )

        answer = (
            "I encountered an error while "
            "generating the final response."
        )

    # =========================================================
    # 6. COLLECT SOURCES
    # =========================================================

    sources = []

    for output in all_outputs:

        if not isinstance(output, dict):
            continue

        output_sources = output.get(
            "sources",
            []
        )

        if not isinstance(output_sources, list):
            continue

        for source in output_sources:

            # ---------------------------------------------
            # Dictionary source
            # ---------------------------------------------

            if isinstance(source, dict):

                clean_source = dict(source)

                sources.append(
                    clean_source
                )

            # ---------------------------------------------
            # String source
            # ---------------------------------------------

            elif isinstance(source, str):

                source = source.strip()

                if not source:
                    continue

                sources.append(
                    {
                        "type": "web",
                        "url": source
                    }
                )

    # =========================================================
    # 7. NORMALIZE SOURCES
    # =========================================================

    normalized_sources = []

    for source in sources:

        if not isinstance(source, dict):
            continue

        clean_source = {}

        # Keep source type
        if source.get("type"):
            clean_source["type"] = source["type"]

        # Keep title
        if source.get("title"):
            clean_source["title"] = source["title"]

        # Handle URL
        if source.get("url"):

            url = source["url"]

            # Prevent malformed nested Markdown URLs
            if (
                isinstance(url, str)
                and url.startswith("[")
                and "](" in url
                and url.endswith(")")
            ):

                try:

                    url = url.split("](")[1][:-1]

                except Exception:
                    pass

            clean_source["url"] = url

        # Document filename/source
        if source.get("source"):
            clean_source["source"] = source["source"]

        if source.get("filename"):
            clean_source["filename"] = source["filename"]

        # If nothing useful remains, skip it
        if clean_source:

            normalized_sources.append(
                clean_source
            )

    # =========================================================
    # 8. REMOVE DUPLICATE SOURCES
    # =========================================================

    unique_sources = []

    seen = set()

    for source in normalized_sources:

        # Prefer URL as unique identifier
        key = (
            source.get("url")
            or source.get("source")
            or source.get("filename")
            or str(source)
        )

        if key in seen:
            continue

        seen.add(key)

        unique_sources.append(
            source
        )

    # =========================================================
    # 9. FINAL RESULT
    # =========================================================

    return {
        "answer": answer,
        "sources": unique_sources
    }

