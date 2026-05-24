from src.schemas import RetrievedChunk
from src.vector_store import get_vector_store


def search_documents(query: str, k: int = 5) -> list[RetrievedChunk]:
    """Return the top-k semantically relevant chunks for a query."""
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_relevance_scores(query, k=k)

    return [
        RetrievedChunk(
            chunk_id=doc.metadata["chunk_id"],
            text=doc.page_content,
            source=doc.metadata["source"],
            page=doc.metadata.get("page"),
            score=score,
        )
        for doc, score in results
    ]
