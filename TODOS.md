# Testing TODOs

This plan starts with the tests that give the most practical value for this project. The goal is to cover real ingestion behavior first, then add a small amount of schema validation coverage.

## 1. Set up the test file structure

- Create `tests/test_ingestion.py`.
- Create `tests/test_schemas.py`.
- Keep ingestion and schema tests separate so the purpose of each file stays clear.

## 2. Write path validation tests first

Target: `src.ingestion.validate_file_path`

- Test that a valid file path returns a `Path` object.
- Test that a missing file raises `FileNotFoundError`.
- Test that a directory path raises `ValueError`.

Why first:
- These are simple tests.
- They verify behavior that every ingestion path depends on.

## 3. Test plain-text ingestion next

Target: `src.ingestion.extract_text_from_plain_file`

- Test that a `.txt` file with text returns one `ExtractedPage`.
- Test that a `.md` file with text returns one `ExtractedPage`.
- Test that leading and trailing whitespace is stripped.
- Test that an empty file returns an empty list.
- Test that `source` is set to the file name.
- Test that `page` is `None` for plain-text files.

Why next:
- These tests are easy to write with temporary files.
- They cover important app behavior without needing PDF setup.

## 4. Test dispatch behavior

Target: `src.ingestion.extract_document_text`

- Test that a `.txt` file is routed to plain-text extraction.
- Test that a `.md` file is routed to plain-text extraction.
- Test that a `.pdf` file is routed to PDF extraction.
- Test that unsupported file types raise `ValueError`.
- Test that uppercase suffixes like `.TXT` still work.

Why here:
- Dispatch logic is small, but important.
- It protects the main ingestion entry point from regressions.

## 5. Add PDF ingestion tests after the plain-text path is stable

Target: `src.ingestion.extract_text_from_pdf`

- Test that a PDF with text returns one or more `ExtractedPage` objects.
- Test that page numbers start at `1`.
- Test that blank PDF pages are skipped.
- Test that `source` is set to the file name.
- Test that extracted text is stripped.

Suggested approach:
- Prefer a tiny fixture PDF stored under `tests/fixtures/` if that keeps the tests simpler.
- If creating PDFs inside tests is easy in this repo, that is also fine.

Why not first:
- PDF tests are a little more setup-heavy.
- They are valuable, but not the easiest entry point if you are still getting comfortable with testing.

## 6. Add a few focused schema tests

Target: `src.schemas`

Write only small, high-value checks:

- Test that `ExtractedPage` rejects empty `text`.
- Test that `DocumentChunk` rejects empty `text`.
- Test that `DocumentChunk` rejects negative `chunk_index`.
- Test that valid model data is accepted for each schema.

Why keep this small:
- Pydantic already covers much of the basic validation machinery.
- These tests should confirm your intended constraints, not duplicate Pydantic itself.

## 7. Add edge-case tests if behavior changes later

Only add these when the code grows and the behavior becomes important:

- Files with invalid UTF-8 bytes should still ingest because of `errors="replace"`.
- Very large text files.
- PDFs with mixed blank and non-blank pages.
- Hidden files or unusual file names.

## 8. Run tests in small batches while building

- Run `pytest tests/test_ingestion.py` while writing ingestion tests.
- Run `pytest tests/test_schemas.py` after adding schema tests.
- Run full `pytest` once everything passes.

Why this helps:
- Smaller runs make failures easier to understand.
- It is less overwhelming when you are new to testing.

## Recommended order to actually implement

1. `validate_file_path`
2. `extract_text_from_plain_file`
3. `extract_document_text`
4. `extract_text_from_pdf`
5. Small schema validation tests

## Definition of done

- The main ingestion paths are covered.
- Unsupported and missing-file behavior is tested.
- Blank content handling is tested.
- Schema validation has a few intentional checks, but does not dominate the suite.
- Tests are readable enough that future changes to ingestion behavior are easy to review.
