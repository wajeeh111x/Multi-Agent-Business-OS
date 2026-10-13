from app.rag.loader import load_pdf

pdf_path = "D:\\AI-Business-OS\\backend\\uploads\\company.pdf"

text = load_pdf(pdf_path)

print("=" * 50)
print(text)
print("=" * 50)