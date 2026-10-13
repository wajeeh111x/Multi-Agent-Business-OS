from app.rag.loader import load_pdf
from app.rag.splitter import split_text
from app.rag.embeddings import create_embeddings

text = load_pdf("D:\\AI-Business-OS\\backend\\uploads\\company.pdf")

chunks = split_text(text)

embeddings = create_embeddings(chunks)

print("Chunks:", len(chunks))
print("Embeddings:", len(embeddings))
print("Vector Size:", len(embeddings[0]))