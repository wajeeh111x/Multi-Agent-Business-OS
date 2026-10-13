from app.ai.ollama_client import ask_llm


def chat_agent(message: str, history: str = ""):
    """
    General conversation agent.

    Handles:
    - Greetings
    - General questions
    - Small talk
    - Questions that do not require tools
    """

    prompt = f"""
You are Business OS AI.

You are a helpful, friendly, and professional AI assistant.

Conversation History:
{history}

Current User Message:
{message}

Instructions:
- Answer naturally.
- Be concise unless the user asks for detail.
- Do not invent information.
- Do not mention tools, planning, or internal reasoning.
- If the user asks about something requiring documents or web search, simply answer with your existing knowledge.

Assistant:
"""

    try:
        answer = ask_llm(prompt)

        return {
            "answer": answer,
            "sources": []
        }

    except Exception as e:
        return {
            "answer": f"Chat Agent Error: {str(e)}",
            "sources": []
        }