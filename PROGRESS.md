# Project Progress

## Current Status

The project now has a working Streamlit app on top of the RAG pipeline, including document upload, ingestion, vector-store indexing, LangGraph-based question answering, and UI rendering of grounded results and retrieved evidence.

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
- Implemented [prompts.py](src/prompts.py) with centralized prompt templates for query planning, evidence evaluation, grounded answers, and quiz generation
- Added prompt rules that reinforce evidence-only answers, missing-evidence handling, and citation expectations
- Added `AgentState` to [schemas.py](src/schemas.py) so the LangGraph workflow has an explicit typed state contract
- Created [agent.py](src/agent.py) as the orchestration layer for the agentic RAG workflow
- Added a shared `ChatOpenAI` instance in [agent.py](src/agent.py) with `temperature=0` for reliability-focused planning, evaluation, retrying, and answer generation
- Implemented structured planner output with `QueryPlan` and `llm.with_structured_output(...)`
- Implemented structured retry-planner output with `RetryQueryPlan`
- Implemented structured evaluator output with `EvidenceEvaluation`
- Implemented `format_evidence()` to render retrieved chunks into a prompt-friendly evidence block with source, page, chunk ID, and text
- Implemented `plan_queries()` to turn the user question into retrieval-friendly search queries with fallback to the original question
- Upgraded planning from raw text parsing to structured output after discussing reliability tradeoffs
- Implemented `retrieve_evidence()` to run retrieval across multiple queries, deduplicate by `chunk_id`, and count retrieval attempts
- Improved retrieval to preserve useful chunks across retries instead of replacing earlier evidence
- Implemented `evaluate_evidence()` to decide whether the evidence is sufficient using structured evaluator output
- Implemented `rewrite_queries_for_retry()` to generate better retry queries using the question, previous queries, and retrieved evidence
- Moved the retry prompt into [prompts.py](src/prompts.py) to keep prompt definitions centralized and reviewable
- Implemented `generate_answer()` to choose between grounded answer generation and quiz generation based on the user request
- Implemented `decide_next_step()` to enforce the workflow retry policy:
  - answer immediately when evidence is sufficient
  - answer after the retry limit is reached
  - otherwise rewrite queries and retry retrieval
- Implemented `build_agent_graph()` with the full LangGraph flow:
  - `plan_queries -> retrieve_evidence -> evaluate_evidence`
  - conditional branch to `generate_answer` or `rewrite_queries_for_retry`
  - retry loop back into retrieval
  - `generate_answer -> END`
- Added `agent_app = build_agent_graph()` so the compiled graph is created once and reused
- Implemented `answer_question(question)` as the public workflow entrypoint that initializes state and invokes the compiled graph
- Added console tracing in [agent.py](src/agent.py) for learning/debugging:
  - prints each node name as the graph runs
  - prints planned queries
  - prints retrieved chunk summaries
  - prints evaluator decisions and retry decisions
  - prints answer-generation completion
- Created [tests/test_agent.py](tests/test_agent.py)
- Added [tests/conftest.py](tests/conftest.py) so pytest can import the local `src` package reliably
- Tested evidence formatting behavior
- Tested planner structured output, whitespace trimming, and fallback behavior
- Tested retrieval deduplication across multiple queries
- Tested retrieval accumulation across retries
- Tested retrieval attempt counting when no chunks are found
- Tested evaluator branching behavior with structured sufficiency output
- Tested retry-query rewriting behavior and fallback behavior
- Tested answer-generation prompt routing for normal answers and quiz requests
- Tested `decide_next_step()` for all three workflow outcomes
- Tested LangGraph compilation and mocked happy-path execution
- Tested `answer_question()` initial-state construction and graph invocation
- Verified targeted workflow tests pass repeatedly with `uv run pytest tests/test_agent.py`
- Updated [agentic_rag_implementation_guide.md](agentic_rag_implementation_guide.md) with optional improvements discovered during implementation:
  - preserving query history across retries
  - documenting the tradeoff between cheap chunk merging and later evidence filtering
- Added the Streamlit app entrypoint in [app.py](app.py)
- Created a Streamlit layout with:
  - a sidebar for document upload and ingestion
  - a main question input area
  - persisted answer and evidence display
- Added startup creation of the upload directory with `Path(UPLOAD_DIR).mkdir(...)`
- Implemented `_ensure_session_state()` so ingestion feedback and the latest question/answer survive Streamlit reruns
- Implemented `_ingest_uploaded_files()` to:
  - save uploaded files into the configured upload directory
  - extract text from PDF, TXT, and Markdown files
  - chunk document text
  - index chunks into the vector store
  - collect per-file success and error messages
  - track the total number of chunks added
- Implemented `_display_ingestion_messages()` to render persisted ingestion feedback in the sidebar
- Implemented `_run_question()` to validate the prompt, execute `answer_question()`, and persist the latest workflow result
- Implemented `_render_result()` to display:
  - the final answer
  - the original question
  - evidence sufficiency and retrieval-attempt metadata
  - the planned search queries
  - the retrieved evidence with source, page, score, and chunk text
- Connected the Streamlit app end-to-end to the ingestion, chunking, vector-store, and LangGraph workflow modules
- Added a user-facing empty-question warning in the app
- Added a user-facing empty-upload warning in the app
- Added a loading spinner around workflow execution in the app
- Configured the Streamlit page title, icon, and wide layout
- Added a document-ingestion action flow that supports multiple uploaded files in one run
- Added sample verification material under [Sample/](Sample/) to manually check the Streamlit app
- Added [Sample/agentic_rag_test_questions.md](Sample/agentic_rag_test_questions.md) as a ready-made manual test question set

## Step 12 Implementation History

This conversation thread completed the LangGraph workflow in a teaching-first sequence rather than writing one large file all at once.

Implementation order used:

1. Defined the workflow state shape with `AgentState`
2. Created the `agent.py` orchestration module
3. Added the shared LLM setup
4. Implemented evidence formatting
5. Implemented planning
6. Implemented retrieval
7. Implemented evidence evaluation
8. Implemented retry query rewriting
9. Implemented answer generation
10. Implemented branch decision logic
11. Built the compiled LangGraph workflow
12. Added the reusable `agent_app`
13. Added the public `answer_question()` wrapper
14. Added focused tests alongside each step
15. Added inspectable console output for learning

Important design decisions made during implementation:

- Prefer structured output for internal workflow/control-flow LLM calls such as planning, retry query rewriting, and evidence evaluation
- Keep free-form output for the final user-facing answer and quiz generation
- Preserve retrieved chunks across retries by merging unique chunks instead of discarding earlier useful evidence
- Keep retry memory simple for the MVP by storing only the latest query set, while documenting query-history improvements for future multi-retry workflows
- Add lightweight console tracing so the graph path and intermediate state are visible during manual runs

## Current Schemas

- `ExtractedPage`: raw text extracted from a file before chunking
- `DocumentChunk`: chunked text ready for embedding and storage
- `RetrievedChunk`: retrieved search result with optional relevance metadata
- `AgentState`: shared LangGraph workflow state for question, rewritten queries, retrieved chunks, evidence sufficiency, answer text, and attempt count

## Current App State

- Users can upload `pdf`, `txt`, and `md` files from the sidebar
- Uploaded files are saved locally, ingested, chunked, and added to Chroma
- Users can ask a question in the main panel and run the LangGraph workflow
- The UI shows the final answer, workflow metadata, planned queries, and retrieved evidence
- Ingestion feedback persists across reruns through Streamlit session state
- The latest answer also persists across reruns through Streamlit session state
- The app can be manually checked with the sample content and question set stored under [Sample/](Sample/)

## Next Step

Manually exercise the Streamlit app with the sample files in [Sample/](Sample/) and evaluate answer quality, citation behavior, and failure handling when evidence is weak or missing.

## After That

- strengthen answer grounding and citation validation
- add duplicate-file protection during ingestion
- consider a grounding report in the UI
- decide later whether to keep console tracing always-on or gate it behind a debug flag
