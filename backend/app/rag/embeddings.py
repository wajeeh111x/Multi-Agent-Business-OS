from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks(chunks):
    """
    Convert text chunks into embeddings.
    """
    embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    )

    return embeddings