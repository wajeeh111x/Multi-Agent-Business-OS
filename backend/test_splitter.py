from app.rag.loader import load_pdf
from app.rag.splitter import split_text

text = load_pdf("D:\\AI-Business-OS\\backend\\uploads\\company.pdf")

chunks = split_text(text)

print(f"Chunks: {len(chunks)}")

for i, chunk in enumerate(chunks):
    print("=" * 60)
    print(f"Chunk {i+1}")
    print(chunk)