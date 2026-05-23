import pytest
from pydantic import ValidationError

from src.schemas import DocumentChunk, ExtractedPage, RetrievedChunk


def test_extracted_page_rejects_empty_text() -> None:
    """Extracted pages should require at least one character of text."""
    with pytest.raises(ValidationError, match="at least 1 character"):
        ExtractedPage(text="", source="sample.txt", page=1)


def test_document_chunk_rejects_empty_text() -> None:
    """Searchable chunks should not allow empty text."""
    with pytest.raises(ValidationError, match="at least 1 character"):
        DocumentChunk(
            chunk_id="chunk-1",
            text="",
            source="sample.txt",
            page=1,
            chunk_index=0,
        )


def test_document_chunk_rejects_negative_chunk_index() -> None:
    """Chunk indexes should start at zero and never be negative."""
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        DocumentChunk(
            chunk_id="chunk-1",
            text="Chunk text",
            source="sample.txt",
            page=1,
            chunk_index=-1,
        )


def test_extracted_page_accepts_valid_data() -> None:
    """A valid extracted page should be created successfully."""
    page = ExtractedPage(
        text="Page text",
        source="sample.txt",
        page=2,
    )

    assert page.text == "Page text"
    assert page.source == "sample.txt"
    assert page.page == 2


def test_document_chunk_accepts_valid_data() -> None:
    """A valid document chunk should keep all provided metadata."""
    chunk = DocumentChunk(
        chunk_id="chunk-1",
        text="Chunk text",
        source="sample.txt",
        page=3,
        chunk_index=0,
    )

    assert chunk.chunk_id == "chunk-1"
    assert chunk.text == "Chunk text"
    assert chunk.source == "sample.txt"
    assert chunk.page == 3
    assert chunk.chunk_index == 0


def test_retrieved_chunk_accepts_valid_data() -> None:
    """A valid retrieved chunk should allow optional score metadata."""
    chunk = RetrievedChunk(
        chunk_id="chunk-1",
        text="Retrieved text",
        source="sample.txt",
        page=4,
        score=0.87,
    )

    assert chunk.chunk_id == "chunk-1"
    assert chunk.text == "Retrieved text"
    assert chunk.source == "sample.txt"
    assert chunk.page == 4
    assert chunk.score == 0.87
