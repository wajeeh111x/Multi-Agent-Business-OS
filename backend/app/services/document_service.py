import os
import shutil

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document

from app.rag.loader import load_pdf
from app.rag.splitter import split_text
from app.rag.embeddings import embed_chunks
from app.rag.vector_store import add_chunks

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_document(db: Session, file: UploadFile, user_id: int):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ---------- RAG ----------
    text = load_pdf(file_path)
    print("Characters:", len(text))

    chunks = split_text(text)
    print("Chunks:", len(chunks))

    embeddings = embed_chunks(chunks)
    print("Embeddings:", len(embeddings))

    add_chunks(
        chunks,
        embeddings,
        file.filename
    )
    # -------------------------

    document = Document(
        filename=file.filename,
        filepath=file_path,
        uploaded_by=user_id
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document