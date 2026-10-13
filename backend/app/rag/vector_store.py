import chromadb

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def add_chunks(chunks, embeddings, filename):
    ids = []

    metadatas = []

    for i in range(len(chunks)):
        ids.append(f"{filename}_{i}")

        metadatas.append(
            {
                "source": filename,
                "chunk": i
            }
        )

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )