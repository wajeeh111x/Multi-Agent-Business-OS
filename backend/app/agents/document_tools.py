from sqlalchemy.orm import Session
from app.models.document import Document


def list_documents(db: Session, user_id: int):

    return (
        db.query(Document)
        .filter(Document.uploaded_by == user_id)
        .all()
    )