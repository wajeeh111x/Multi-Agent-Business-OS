from app.ai.ollama_client import ask_llm


def should_retry(outputs):

    retry_keywords = [
        "no document found",
        "unknown tool",
        "error",
        "failed",
        "exception",
        "not found",
        "unable"
    ]

    for output in outputs:

        answer = output.get("answer", "").lower()

        if any(keyword in answer for keyword in retry_keywords):
            return True

    return False


def reflect(message, outputs):

    prompt = f"""
You are an AI agent reviewer.

The user asked:

{message}

The tools returned:

{outputs}

Decide whether another tool should be executed.

Answer ONLY:

YES

or

NO
"""

    answer = ask_llm(prompt).strip().upper()

    return answer == "YES"