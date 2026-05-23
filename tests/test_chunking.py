from src.chunking import chunk_pages
from src.schemas import ExtractedPage


def test_chunk_pages_returns_chunks_for_long_text() -> None:
    """Long input should be split into one or more searchable chunks."""
    pages = [
        ExtractedPage(
            text="This is a test document. " * 100,
            source="test.txt",
            page=1,
        )
    ]

    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    assert chunks[0].source == "test.txt"
    assert chunks[0].page == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].chunk_id == "test.txt::page-1::chunk-0"


def test_chunk_pages_preserves_page_metadata_across_multiple_pages() -> None:
    """Chunk metadata should keep the original source and page for each page."""
    pages = [
        ExtractedPage(text="Alpha " * 60, source="multi.pdf", page=2),
        ExtractedPage(text="Beta " * 60, source="multi.pdf", page=5),
    ]

    chunks = chunk_pages(pages, chunk_size=80, chunk_overlap=10)

    page_two_chunks = [chunk for chunk in chunks if chunk.page == 2]
    page_five_chunks = [chunk for chunk in chunks if chunk.page == 5]

    assert page_two_chunks
    assert page_five_chunks
    assert all(chunk.source == "multi.pdf" for chunk in chunks)
    assert page_two_chunks[0].chunk_id == "multi.pdf::page-2::chunk-0"
    assert page_five_chunks[0].chunk_id == "multi.pdf::page-5::chunk-0"


def test_chunk_pages_returns_empty_list_for_no_pages() -> None:
    """No extracted pages should produce no chunks."""
    assert chunk_pages([]) == []
