from app.rag.embeddings import model
from app.rag.vector_store import collection


def retrieve(query: str, n_results: int = 5):
    """
    Search ChromaDB for the most relevant chunks.
    """

    query_embedding = model.encode(
        query,
        convert_to_numpy=True
    )

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )

    return results