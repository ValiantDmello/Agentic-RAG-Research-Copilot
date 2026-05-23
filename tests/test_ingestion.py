from pathlib import Path

import pytest

from src.ingestion import (
    extract_document_text,
    extract_text_from_pdf,
    extract_text_from_plain_file,
    validate_file_path,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_validate_file_path_returns_path_for_existing_file() -> None:
    """A real fixture file should come back as a Path object."""
    sample_file = FIXTURES_DIR / "supported_text" / "sample.txt"

    result = validate_file_path(str(sample_file))

    assert result == sample_file
    assert isinstance(result, Path)


def test_validate_file_path_raises_for_missing_file() -> None:
    """A path that does not exist should raise a clear file-not-found error."""
    missing_file = FIXTURES_DIR / "supported_text" / "does_not_exist.txt"

    with pytest.raises(FileNotFoundError, match="File does not exist"):
        validate_file_path(str(missing_file))


def test_validate_file_path_raises_for_directory() -> None:
    """A directory fixture is not a valid input because ingestion expects a file."""
    directory_path = FIXTURES_DIR / "supported_text"

    with pytest.raises(ValueError, match="Path is not a file"):
        validate_file_path(str(directory_path))


def test_extract_text_from_plain_file_returns_one_page_for_txt_file() -> None:
    """A non-empty text file should be returned as one extracted page."""
    sample_file = FIXTURES_DIR / "supported_text" / "sample.txt"

    pages = extract_text_from_plain_file(str(sample_file))

    assert len(pages) == 1
    assert pages[0].text.startswith("RAG ingestion sample text fixture.")
    assert pages[0].source == "sample.txt"
    assert pages[0].page is None


def test_extract_text_from_plain_file_returns_one_page_for_md_file() -> None:
    """Markdown files use the same plain-text ingestion path."""
    sample_file = FIXTURES_DIR / "supported_text" / "sample.md"

    pages = extract_text_from_plain_file(str(sample_file))

    assert len(pages) == 1
    assert pages[0].text.startswith("# RAG Fixture Markdown")
    assert "## Key points" in pages[0].text
    assert pages[0].source == "sample.md"
    assert pages[0].page is None


def test_extract_text_from_plain_file_strips_leading_and_trailing_whitespace() -> None:
    """Outer whitespace should be trimmed, while inner content stays intact."""
    sample_file = FIXTURES_DIR / "supported_text" / "leading_trailing_spaces.txt"

    pages = extract_text_from_plain_file(str(sample_file))

    assert len(pages) == 1
    assert pages[0].text == (
        "Leading spaces should be stripped.\n"
        "Middle line remains.\n"
        "Trailing spaces should be stripped."
    )


def test_extract_text_from_plain_file_returns_empty_list_for_blank_txt_file() -> None:
    """A blank text file should not produce an empty extracted page."""
    sample_file = FIXTURES_DIR / "supported_text" / "blank.txt"

    pages = extract_text_from_plain_file(str(sample_file))

    assert pages == []


def test_extract_text_from_plain_file_returns_empty_list_for_blank_md_file() -> None:
    """A blank markdown file should also return no extracted pages."""
    sample_file = FIXTURES_DIR / "supported_text" / "blank.md"

    pages = extract_text_from_plain_file(str(sample_file))

    assert pages == []


def test_extract_text_from_plain_file_returns_empty_list_for_whitespace_only_file() -> None:
    """Whitespace-only content becomes empty after strip and should be skipped."""
    sample_file = FIXTURES_DIR / "supported_text" / "whitespace_only.txt"

    pages = extract_text_from_plain_file(str(sample_file))

    assert pages == []


def test_extract_text_from_pdf_returns_one_page_for_single_page_pdf() -> None:
    """A PDF with text on one page should return one extracted page."""
    sample_file = FIXTURES_DIR / "supported_pdf" / "sample.pdf"

    pages = extract_text_from_pdf(str(sample_file))

    assert len(pages) == 1
    assert pages[0].page == 1
    assert pages[0].source == "sample.pdf"
    assert pages[0].text.startswith("PDF sample fixture.")
    assert "Source marker: sample.pdf page 1." in pages[0].text


def test_extract_text_from_pdf_returns_all_non_empty_pages_in_order() -> None:
    """A multi-page PDF should preserve page order and page-number metadata."""
    sample_file = FIXTURES_DIR / "supported_pdf" / "multi_page.pdf"

    pages = extract_text_from_pdf(str(sample_file))

    assert len(pages) == 3
    assert [page.page for page in pages] == [1, 2, 3]
    assert all(page.source == "multi_page.pdf" for page in pages)
    assert pages[0].text.startswith("Multi-page PDF fixture.")
    assert "Source marker: multi_page.pdf page 2." in pages[1].text
    assert "Final page sentinel: blue-lantern-17." in pages[2].text


def test_extract_text_from_pdf_skips_blank_first_page_and_keeps_real_page_number() -> None:
    """Blank pages should be skipped without renumbering the later text page."""
    sample_file = FIXTURES_DIR / "supported_pdf" / "blank_first_page_then_text.pdf"

    pages = extract_text_from_pdf(str(sample_file))

    assert len(pages) == 1
    assert pages[0].page == 2
    assert pages[0].source == "blank_first_page_then_text.pdf"
    assert "This text appears on page 2 only." in pages[0].text


def test_extract_text_from_pdf_skips_trailing_blank_pages() -> None:
    """A blank page after text should not create an empty extracted page."""
    sample_file = FIXTURES_DIR / "supported_pdf" / "text_then_blank_page.pdf"

    pages = extract_text_from_pdf(str(sample_file))

    assert len(pages) == 1
    assert pages[0].page == 1
    assert pages[0].source == "text_then_blank_page.pdf"
    assert "Page 2 is intentionally blank." in pages[0].text


def test_extract_text_from_pdf_returns_empty_list_for_blank_pdf() -> None:
    """A completely blank PDF should return no extracted pages."""
    sample_file = FIXTURES_DIR / "supported_pdf" / "blank.pdf"

    pages = extract_text_from_pdf(str(sample_file))

    assert pages == []


def test_extract_document_text_dispatches_txt_files_to_plain_text_extraction() -> None:
    """The main ingestion entry point should handle .txt files."""
    sample_file = FIXTURES_DIR / "supported_text" / "sample.txt"

    pages = extract_document_text(str(sample_file))

    assert len(pages) == 1
    assert pages[0].source == "sample.txt"
    assert pages[0].page is None
    assert pages[0].text.startswith("RAG ingestion sample text fixture.")


def test_extract_document_text_dispatches_md_files_to_plain_text_extraction() -> None:
    """The main ingestion entry point should handle .md files."""
    sample_file = FIXTURES_DIR / "supported_text" / "sample.md"

    pages = extract_document_text(str(sample_file))

    assert len(pages) == 1
    assert pages[0].source == "sample.md"
    assert pages[0].page is None
    assert pages[0].text.startswith("# RAG Fixture Markdown")


def test_extract_document_text_dispatches_pdf_files_to_pdf_extraction() -> None:
    """The main ingestion entry point should handle .pdf files."""
    sample_file = FIXTURES_DIR / "supported_pdf" / "sample.pdf"

    pages = extract_document_text(str(sample_file))

    assert len(pages) == 1
    assert pages[0].source == "sample.pdf"
    assert pages[0].page == 1
    assert pages[0].text.startswith("PDF sample fixture.")


def test_extract_document_text_accepts_uppercase_text_extensions() -> None:
    """Extension matching should be case-insensitive for supported text files."""
    sample_file = FIXTURES_DIR / "supported_text" / "uppercase_extension.TXT"

    pages = extract_document_text(str(sample_file))

    assert len(pages) == 1
    assert pages[0].source == "uppercase_extension.TXT"
    assert pages[0].page is None
    assert "case-insensitive" in pages[0].text


def test_extract_document_text_accepts_uppercase_pdf_extensions() -> None:
    """Extension matching should be case-insensitive for supported PDF files."""
    sample_file = FIXTURES_DIR / "supported_pdf" / "uppercase_extension.PDF"

    pages = extract_document_text(str(sample_file))

    assert len(pages) == 1
    assert pages[0].source == "uppercase_extension.PDF"
    assert pages[0].page == 1
    assert "case-insensitive" in pages[0].text


def test_extract_document_text_raises_for_unsupported_file_type() -> None:
    """Unsupported suffixes should raise a clear error at the dispatch layer."""
    sample_file = FIXTURES_DIR / "unsupported" / "sample.json"

    with pytest.raises(ValueError, match=r"Unsupported file type: \.json"):
        extract_document_text(str(sample_file))
