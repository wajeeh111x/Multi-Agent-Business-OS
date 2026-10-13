def build_prompt(question: str, retrieved_docs):
    """
    Build a prompt for Ollama using retrieved document chunks.
    """

    documents = retrieved_docs["documents"][0]

    context = "\n\n".join(documents)

    prompt = f"""
You are an AI assistant.

Answer ONLY using the context below.

If the answer is not in the context, say:

"I couldn't find that information in the uploaded documents."

----------------------

Context:

{context}

----------------------

Question:

{question}

Answer:
"""

    return prompt