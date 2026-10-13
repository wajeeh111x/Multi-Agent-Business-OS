from app.ai.ollama_client import ask_llm

prompt = """
Context:

The office starts at 9 AM.
Employees receive 20 annual leaves.

Question:

When does the office start?

Answer:
"""

print(ask_llm(prompt))