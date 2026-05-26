# Agentic RAG Research Copilot

This repository contains a reliability-focused Agentic RAG application that ingests local documents, stores chunk embeddings in Chroma, retrieves grounded evidence, and answers questions through a LangGraph workflow and Streamlit UI.

The current implementation supports PDF, TXT, and Markdown ingestion, semantic retrieval, retry-aware query planning, evidence sufficiency checks, and answer generation with source-aware context passed into the model.

## What It Does

- Upload `pdf`, `txt`, and `md` files through the Streamlit app
- Extract document text with PyMuPDF for PDFs and UTF-8 fallback reading for plain-text files
- Split documents into overlapping chunks for embedding and retrieval
- Store chunks in a persistent local Chroma vector store
- Plan 1 to 4 retrieval queries from the user question
- Retrieve and deduplicate evidence across queries
- Evaluate whether the retrieved evidence is sufficient
- Retry retrieval once with refined queries when evidence is weak
- Generate a final answer or a quiz from the retrieved evidence
- Run a structured grounding check on the generated answer
- Show retrieved evidence, query plan, and workflow metadata in the UI

## Tech Stack

- Python 3.11+
- Streamlit
- LangGraph
- LangChain
- OpenAI API
- ChromaDB
- PyMuPDF
- Pydantic
- Pytest
- `uv` for environment and dependency management

## Project Structure

```text
rag-project/
|-- app.py
|-- src/
|   |-- agent.py
|   |-- chunking.py
|   |-- config.py
|   |-- ingestion.py
|   |-- prompts.py
|   |-- retriever.py
|   |-- schemas.py
|   |-- vector_store.py
|   `-- vector_store_utils.py
|-- tests/
|-- Sample/
|-- .env.example
|-- PROGRESS.md
|-- agentic_rag_implementation_guide.md
`-- pyproject.toml
```

## Requirements

- Python `3.11` or newer
- An OpenAI API key
- `uv` installed locally

## Setup

1. Create the virtual environment:

```powershell
uv venv
```

2. Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
uv sync
```

4. Create your environment file:

```powershell
Copy-Item .env.example .env
```

5. Edit `.env` and set your real OpenAI key.

Example `.env` values:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHROMA_DIR=data/chroma
UPLOAD_DIR=data/uploads
```

## Running the App

Start the Streamlit UI with:

```powershell
uv run streamlit run app.py
```

Then open the local URL shown in the terminal, typically `http://localhost:8501`.

## How to Use It

1. Open the Streamlit app.
2. Upload one or more `pdf`, `txt`, or `md` files from the sidebar.
3. Click `Ingest Documents`.
4. Ask a question in the main panel.
5. Review the generated answer, retrieval attempts, search queries, and retrieved evidence.
6. Review the grounding check for unsupported claims and safer wording guidance.

The app also routes questions containing `quiz` through a quiz-generation prompt.

## Workflow Overview

The LangGraph workflow in [src/agent.py](src/agent.py) currently follows this flow:

1. `plan_queries`
2. `retrieve_evidence`
3. `evaluate_evidence`
4. If evidence is sufficient, `generate_answer`
5. Otherwise, `rewrite_queries_for_retry`
6. Run retrieval once more, then answer

Important behavior:

- Retrieval results are deduplicated by `chunk_id`
- Useful chunks are preserved across retries
- Evidence sufficiency is modeled as a structured boolean output
- Post-answer grounding review is modeled as a structured report
- Console tracing is enabled in the workflow for debugging and learning

## Running Tests

Most of the codebase has targeted unit tests under `tests/`.

Run the full test suite:

```powershell
uv run pytest
```

Run a specific test file:

```powershell
uv run pytest tests/test_agent.py
```

Project note: this repo prefers avoiding broad test runs during feature work unless you explicitly want them. If you add a new test, run only the relevant targeted tests.

## Vector Store Utilities

The repo includes a small CLI for inspecting and managing the local Chroma store in [src/vector_store_utils.py](src/vector_store_utils.py).

Show collection stats:

```powershell
uv run python -m src.vector_store_utils stats
```

List stored metadata:

```powershell
uv run python -m src.vector_store_utils list-metadata --limit 20
```

Delete all chunks from one source file:

```powershell
uv run python -m src.vector_store_utils delete-source my_file.pdf --yes
```

Clear the whole vector store:

```powershell
uv run python -m src.vector_store_utils clear --yes
```

## Sample Material

Manual verification material lives in [Sample/](Sample/). Use it to test ingestion, grounded answers, quiz generation, and weak-evidence behavior.

The repo also includes fixtures under [tests/fixtures/](tests/fixtures/) for ingestion and parser coverage.

## Current Limitations

- Final answer citations are still in the older prompt-driven format, not the stronger stable citation-ID format from Step 18 of the implementation guide
- Retrieval currently uses semantic similarity only; hybrid search and reranking are not implemented
- Duplicate-file protection is not implemented yet
- The app uses local persistent storage and is aimed at single-user local development

## Security and Data Notes

- Do not commit `.env`
- Uploaded files are stored locally under the configured `UPLOAD_DIR`
- Chroma data is stored locally under the configured `CHROMA_DIR`
- Avoid placing sensitive private documents in the repo itself

## Development Notes

- Keep prompts centralized in [src/prompts.py](src/prompts.py)
- Keep schema changes aligned with [src/schemas.py](src/schemas.py)
- Update tests when changing retrieval, chunking, citation behavior, or workflow control flow
- Review [PROGRESS.md](PROGRESS.md) for implementation history and current status
- Review [agentic_rag_implementation_guide.md](agentic_rag_implementation_guide.md) for the step-by-step build plan

## Troubleshooting

`OPENAI_API_KEY is missing`

- Create `.env` from `.env.example`
- Make sure `OPENAI_API_KEY` is set
- Restart the app after editing the file

`ModuleNotFoundError` or dependency issues

- Re-run `uv sync`
- Confirm the virtual environment is activated if you are not using `uv run`

No useful answer is returned

- Check whether the document was ingested successfully
- Expand `Retrieved evidence` in the UI to see what was actually found
- Try a narrower question or a document-specific phrase
