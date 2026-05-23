# Project Progress

## Current Status

The project has been initialized with `uv` and the base repository structure is in place.

## Completed

- Initialized the project with `uv`
- Created the virtual environment
- Added the main dependencies in `pyproject.toml`
- Added the dev dependency for `pytest`
- Created the base folders: `data/`, `src/`, `tests/`
- Added `.env.example`
- Added `.gitignore`
- Added [config.py](/abs/c:/Users/vvd09/OneDrive/Desktop/Vali/Projects/rag-project/src/config.py:1)
- Added [schemas.py](/abs/c:/Users/vvd09/OneDrive/Desktop/Vali/Projects/rag-project/src/schemas.py:1)
- Added [ingestion.py](/abs/c:/Users/vvd09/OneDrive/Desktop/Vali/Projects/rag-project/src/ingestion.py:1)
- Documented schema purposes with short comments
- Documented ingestion behavior with short comments
- Updated setup docs to prefer `uv`
- Implemented PDF text extraction with PyMuPDF
- Implemented TXT and Markdown ingestion
- Normalized ingestion output to `ExtractedPage` models
- Added backend file path validation for missing paths and non-file inputs
- Added clear errors for unsupported file types
- Created [tests/test_ingestion.py](/abs/c:/Users/vvd09/OneDrive/Desktop/Vali/Projects/rag-project/tests/test_ingestion.py:1)
- Created [tests/test_schemas.py](/abs/c:/Users/vvd09/OneDrive/Desktop/Vali/Projects/rag-project/tests/test_schemas.py:1)
- Added fixture-based ingestion tests under `tests/fixtures/`
- Tested `validate_file_path` for valid files, missing files, and directory inputs
- Tested plain-text ingestion for `.txt` and `.md` files
- Tested blank and whitespace-only plain-text files
- Tested PDF ingestion for single-page, multi-page, and blank-page cases
- Tested `extract_document_text` dispatch for supported and unsupported file types
- Tested schema validation for empty text and negative `chunk_index`
- Verified valid creation of `ExtractedPage`, `DocumentChunk`, and `RetrievedChunk`
- Ran ingestion and schema tests successfully in small batches during implementation

## Current Schemas

- `ExtractedPage`: raw text extracted from a file before chunking
- `DocumentChunk`: chunked text ready for embedding and storage
- `RetrievedChunk`: retrieved search result with optional relevance metadata

## Next Step

Implement [chunking.py](/abs/c:/Users/vvd09/OneDrive/Desktop/Vali/Projects/rag-project/src/chunking.py:1) and add focused tests for chunk creation behavior.

## After That

- add `tests/test_chunking.py`
- then move on to vector storage and retrieval
