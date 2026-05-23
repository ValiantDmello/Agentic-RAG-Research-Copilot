from src.schemas import DocumentChunk
from src.vector_store import add_chunks_to_vector_store


class FakeVectorStore:
    def __init__(self) -> None:
        self.calls: list[tuple[list[object], list[str]]] = []

    def add_documents(self, documents: list[object], ids: list[str]) -> None:
        self.calls.append((documents, ids))


def test_add_chunks_to_vector_store_indexes_documents(monkeypatch) -> None:
    """Chunks should be converted into vector-store documents with stable IDs."""
    fake_store = FakeVectorStore()
    chunks = [
        DocumentChunk(
            chunk_id="sample.txt::page-1::chunk-0",
            text="First chunk",
            source="sample.txt",
            page=1,
            chunk_index=0,
        ),
        DocumentChunk(
            chunk_id="sample.txt::page-1::chunk-1",
            text="Second chunk",
            source="sample.txt",
            page=1,
            chunk_index=1,
        ),
    ]

    monkeypatch.setattr("src.vector_store.get_vector_store", lambda: fake_store)

    indexed_count = add_chunks_to_vector_store(chunks)

    assert indexed_count == 2
    assert len(fake_store.calls) == 1

    documents, ids = fake_store.calls[0]

    assert ids == [
        "sample.txt::page-1::chunk-0",
        "sample.txt::page-1::chunk-1",
    ]
    assert documents[0].page_content == "First chunk"
    assert documents[0].metadata == {
        "source": "sample.txt",
        "page": 1,
        "chunk_index": 0,
        "chunk_id": "sample.txt::page-1::chunk-0",
    }
    assert documents[1].page_content == "Second chunk"


def test_add_chunks_to_vector_store_skips_empty_input(monkeypatch) -> None:
    """No chunks should mean no vector-store write call."""
    fake_store = FakeVectorStore()
    monkeypatch.setattr("src.vector_store.get_vector_store", lambda: fake_store)

    indexed_count = add_chunks_to_vector_store([])

    assert indexed_count == 0
    assert fake_store.calls == []
