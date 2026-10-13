from sqlalchemy.orm import Session

from app.models.chat import ChatMessage

from app.rag.retriever import retrieve
from app.rag.prompt import build_prompt
from app.ai.ollama_client import ask_llm


def save_message(
    db: Session,
    user_id: int,
    role: str,
    message: str
):
    chat = ChatMessage(
        user_id=user_id,
        role=role,
        message=message
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


def get_chat_history(
    db: Session,
    user_id: int,
    limit: int = 10
):
    """
    Returns the most recent chat messages for the user.
    """

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )

    # Reverse so oldest appears first
    messages.reverse()

    return messages


def rag_chat(question: str):
    retrieved = retrieve(question)

    prompt = build_prompt(
        question,
        retrieved
    )

    answer = ask_llm(prompt)

    return {
        "answer": answer,
        "sources": retrieved["metadatas"][0]
    }