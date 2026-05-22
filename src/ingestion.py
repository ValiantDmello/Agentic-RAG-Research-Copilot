from pathlib import Path

import fitz

from src.schemas import ExtractedPage


# Plain-text formats we currently support without specialized parsers.
SUPPORTED_PLAIN_TEXT_SUFFIXES = {".txt", ".md"}


def validate_file_path(file_path: str) -> Path:
    """Return a validated file path or raise a clear error."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    return path


def extract_text_from_pdf(file_path: str) -> list[ExtractedPage]:
    """Extract non-empty text from each PDF page."""
    source_path = validate_file_path(file_path)
    pages: list[ExtractedPage] = []

    # Use a context manager so the file handle is always released cleanly.
    with fitz.open(source_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            # Skip blank pages so we do not create empty chunks later.
            if not text:
                continue

            pages.append(
                ExtractedPage(
                    text=text,
                    page=page_number,
                    source=source_path.name,
                )
            )

    return pages


def extract_text_from_plain_file(file_path: str) -> list[ExtractedPage]:
    """Read a plain-text file and return it as one extracted page."""
    source_path = validate_file_path(file_path)

    # "replace" keeps the ingest running even if a file has a few bad bytes.
    text = source_path.read_text(encoding="utf-8", errors="replace").strip()

    if not text:
        return []

    return [
        ExtractedPage(
            text=text,
            page=None,
            source=source_path.name,
        )
    ]


def extract_document_text(file_path: str) -> list[ExtractedPage]:
    """Dispatch extraction based on the file extension."""
    source_path = validate_file_path(file_path)
    suffix = source_path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)

    if suffix in SUPPORTED_PLAIN_TEXT_SUFFIXES:
        return extract_text_from_plain_file(file_path)

    raise ValueError(f"Unsupported file type: {suffix}")
