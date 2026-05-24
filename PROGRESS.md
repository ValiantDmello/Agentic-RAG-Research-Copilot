# Project Progress

## Current Status

The project now has working ingestion, schemas, text chunking, vector-store indexing, and retrieval in place for the RAG pipeline.

## Completed

- Initialized the project with `uv`
- Created the virtual environment
- Added the main dependencies in `pyproject.toml`
- Added the dev dependency for `pytest`
- Created the base folders: `data/`, `src/`, `tests/`
- Added `.env.example`
- Added `.gitignore`
- Added [config.py](src/config.py)
- Added [schemas.py](src/schemas.py)
- Added [ingestion.py](src/ingestion.py)
- Documented schema purposes with short comments
- Documented ingestion behavior with short comments
- Updated setup docs to prefer `uv`
- Implemented PDF text extraction with PyMuPDF
- Implemented TXT and Markdown ingestion
- Normalized ingestion output to `ExtractedPage` models
- Added backend file path validation for missing paths and non-file inputs
- Added clear errors for unsupported file types
- Created [tests/test_ingestion.py](tests/test_ingestion.py)
- Created [tests/test_schemas.py](tests/test_schemas.py)
- Added fixture-based ingestion tests under `tests/fixtures/`
- Tested `validate_file_path` for valid files, missing files, and directory inputs
- Tested plain-text ingestion for `.txt` and `.md` files
- Tested blank and whitespace-only plain-text files
- Tested PDF ingestion for single-page, multi-page, and blank-page cases
- Tested `extract_document_text` dispatch for supported and unsupported file types
- Tested schema validation for empty text and negative `chunk_index`
- Verified valid creation of `ExtractedPage`, `DocumentChunk`, and `RetrievedChunk`
- Ran ingestion and schema tests successfully in small batches during implementation
- Implemented [chunking.py](src/chunking.py) with overlapping text chunking via `RecursiveCharacterTextSplitter`
- Created [tests/test_chunking.py](tests/test_chunking.py)
- Tested long-text chunk splitting behavior
- Tested chunk metadata preservation across multiple source pages
- Tested empty input handling for chunk creation
- Documented the reliable `uv run python -m pytest` test command in `README.md`
- Implemented [vector_store.py](src/vector_store.py) with OpenAI embeddings and persistent Chroma storage
- Added vector-store chunk-to-document conversion with stable `chunk_id` values and retrieval-friendly metadata
- Created [tests/test_vector_store.py](tests/test_vector_store.py)
- Tested vector-store indexing behavior with mocked writes
- Tested empty input handling for vector storage
- Verified vector-store, chunking, and schema tests pass together with `PYTHONPATH=. uv run pytest tests/test_vector_store.py tests/test_chunking.py tests/test_schemas.py`
- Implemented [retriever.py](src/retriever.py) with semantic search over stored chunks
- Returned typed `RetrievedChunk` results including `text`, `source`, `page`, `chunk_id`, and relevance `score`
- Created [tests/test_retriever.py](tests/test_retriever.py)
- Tested retriever behavior with mocked vector-store search results
- Tested empty-result handling for retrieval
- Verified retriever tests pass with `PYTHONPATH=. uv run pytest tests/test_retriever.py`

## Current Schemas

- `ExtractedPage`: raw text extracted from a file before chunking
- `DocumentChunk`: chunked text ready for embedding and storage
- `RetrievedChunk`: retrieved search result with optional relevance metadata

## Next Step

Create the prompt templates and start wiring retrieval into the agent workflow.

## After That

- connect ingestion and chunking into an end-to-end indexing flow
- start wiring the agent workflow and answer grounding
