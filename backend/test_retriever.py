# test_retriever.py

from app.rag.retriever import retrieve

result = retrieve("What is Automatic Zoom?")

print(result)