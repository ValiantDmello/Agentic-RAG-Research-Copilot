# AGENTS.md

## Project Context

This repository is an Agentic RAG application: a document-aware assistant that can ingest files, retrieve relevant evidence, plan multi-step searches, verify grounding, and answer with citations.

The main goal is reliability over creativity. Answers should be based on retrieved source text, and the app should clearly say when the knowledge base does not contain enough evidence.

## Preferred Stack

- Python for backend and agent logic
- LangGraph for agent workflow orchestration
- LangChain or LlamaIndex for RAG utilities
- Chroma or FAISS for local vector storage
- FastAPI for API endpoints
- Streamlit or Next.js for the UI
- Pytest for tests

## Development Rules

- Keep code simple, modular, and readable.
- Separate ingestion, retrieval, agent workflow, evaluation, and UI code.
- Do not hard-code API keys or secrets. Use `.env` and environment variables.
- Add or update tests when changing retrieval, chunking, citation, or agent behavior.
- Prefer small functions with clear names over large agent prompts or monolithic files.
- Use type hints for Python functions where practical.

## RAG and Agent Behavior

- Every final answer should include citations when source documents are used.
- The agent should not invent facts that are not supported by retrieved evidence.
- If retrieval confidence is low, return a cautious answer and explain what is missing.
- Keep prompts versioned in code or prompt files so behavior changes are easy to review.
- Log intermediate steps such as planned sub-questions, retrieved chunks, and grounding checks.

## Suggested Commands

```bash
uv venv
.venv\Scripts\activate
uv sync
uv run pytest
uv run python -m app.main
```

For Streamlit UI:

```bash
uv run streamlit run app/ui.py
```

## Before Finishing a Task

- Check that new code does not expose secrets or private document contents in logs.
- Update README or docs if setup, commands, or architecture changed.
- Keep changes focused on the requested task.


## Additional information
- ./agentic_rag_implementation_guide.md
- ./agentic_rag_srs.md


## Don'ts

- Do not run tests, I always do that manually. In case you are writing new tests, then you are allowed to run only those specific tests.