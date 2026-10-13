from app.rag.loader import load_pdf
from app.rag.splitter import split_text
from app.rag.embeddings import create_embeddings
from app.rag.vector_store import add_chunks

text = load_pdf("D:\\AI-Business-OS\\backend\\uploads\\company.pdf")

chunks = split_text(text)

embeddings = create_embeddings(chunks)

add_chunks(
    chunks,
    embeddings,
    "company.pdf"
)

print("Stored Successfully")