from sqlalchemy.orm import Session
from app.models.chat_message import ChatMessage


def get_last_messages(db: Session, user_id: int, limit=10):

    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.id.desc())
        .limit(limit)
        .all()
    )