from langchain_core.documents import Document

from src.retriever import search_documents


class FakeVectorStore:
    def __init__(self, results: list[tuple[Document, float]]) -> None:
        self.results = results
        self.queries: list[tuple[str, int]] = []

    def similarity_search_with_relevance_scores(
        self,
        query: str,
        k: int,
    ) -> list[tuple[Document, float]]:
        self.queries.append((query, k))
        return self.results


def test_search_documents_returns_retrieved_chunks(monkeypatch) -> None:
    """Retriever results should preserve chunk text, metadata, and score."""
    fake_store = FakeVectorStore(
        results=[
            (
                Document(
                    page_content="Relevant chunk",
                    metadata={
                        "source": "sample.txt",
                        "page": 2,
                        "chunk_id": "sample.txt::page-2::chunk-0",
                    },
                ),
                0.91,
            ),
            (
                Document(
                    page_content="Another chunk",
                    metadata={
                        "source": "sample.txt",
                        "page": None,
                        "chunk_id": "sample.txt::page-none::chunk-1",
                    },
                ),
                0.72,
            ),
        ]
    )

    monkeypatch.setattr("src.retriever.get_vector_store", lambda: fake_store)

    results = search_documents("important question", k=3)

    assert fake_store.queries == [("important question", 3)]
    assert [chunk.chunk_id for chunk in results] == [
        "sample.txt::page-2::chunk-0",
        "sample.txt::page-none::chunk-1",
    ]
    assert results[0].text == "Relevant chunk"
    assert results[0].source == "sample.txt"
    assert results[0].page == 2
    assert results[0].score == 0.91
    assert results[1].page is None


def test_search_documents_returns_empty_list_when_no_matches(monkeypatch) -> None:
    """No vector-store matches should produce an empty retrieval result."""
    fake_store = FakeVectorStore(results=[])
    monkeypatch.setattr("src.retriever.get_vector_store", lambda: fake_store)

    results = search_documents("missing topic")

    assert fake_store.queries == [("missing topic", 5)]
    assert results == []
