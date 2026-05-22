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

## Current Schemas

- `ExtractedPage`: raw text extracted from a file before chunking
- `DocumentChunk`: chunked text ready for embedding and storage
- `RetrievedChunk`: retrieved search result with optional relevance metadata

## Next Step

Add tests for [ingestion.py](/abs/c:/Users/vvd09/OneDrive/Desktop/Vali/Projects/rag-project/src/ingestion.py:1) to verify:

- PDF extraction returns page-level `ExtractedPage` objects
- TXT and Markdown files are ingested as one extracted page
- missing paths and directory inputs raise clear errors
- unsupported file types are rejected with a clear error

## After That

- implement `chunking.py`
- add `tests/test_ingestion.py`
- add `tests/test_chunking.py`
- then move on to vector storage and retrieval
