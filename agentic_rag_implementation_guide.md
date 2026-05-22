# Agentic RAG Research Copilot — Step-by-Step Implementation Guide

## 1. Project Goal

You will build an **Agentic RAG Research Copilot** that lets users upload documents and ask questions about them. The system will retrieve relevant document chunks, evaluate whether the evidence is enough, optionally perform another search, and generate a final answer with citations.

The MVP will use:

- Python
- Streamlit
- LangGraph
- LangChain
- ChromaDB
- OpenAI API
- PyMuPDF for PDF extraction
- python-dotenv for environment variables

### Setup Note: Use `uv` Instead of `pip`

This repository should use `uv` for project creation, virtual environments, dependency installation, and command execution.

Preferred setup flow:

```powershell
uv init --app --python 3.11 .
uv venv
.venv\Scripts\Activate.ps1
uv add streamlit python-dotenv pydantic pymupdf langchain langchain-openai langchain-community langgraph chromadb tiktoken
uv add --dev pytest
```

Prefer `pyproject.toml` and `uv.lock` over `requirements.txt`.

---

## 2. Final MVP Features

By the end, the app should support:

- Uploading PDF, TXT, and Markdown files.
- Extracting document text.
- Splitting text into chunks.
- Creating embeddings.
- Storing chunks in ChromaDB.
- Asking questions through a chat UI.
- Agentic query planning.
- Multi-step retrieval.
- Evidence sufficiency checking.
- Cited answer generation.
- Optional quiz generation.
- Viewing retrieved evidence.

---

## 3. Recommended Folder Structure

Create this structure:

```text
agentic-rag-copilot/
│
├── app.py
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── README.md
│
├── data/
│   ├── uploads/
│   └── chroma/
│
├── src/
│   ├── __init__.py
│   │
│   ├── config.py
│   ├── ingestion.py
│   ├── chunking.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── prompts.py
│   ├── agent.py
│   ├── schemas.py
│   └── utils.py
│
└── tests/
    ├── test_chunking.py
    ├── test_ingestion.py
    └── test_retriever.py
```

---

## 4. Step 1 — Create the Project

Open a terminal and run:

```powershell
mkdir agentic-rag-copilot
cd agentic-rag-copilot
uv init --app --python 3.11 .
mkdir data, data/uploads, data/chroma, src, tests
```

Create Python package files:

```powershell
New-Item -ItemType File src/__init__.py
```

---

## 5. Step 2 — Create a Virtual Environment

Use `uv` to create the virtual environment:

```bash
uv venv
```

### macOS/Linux

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

---

## 6. Step 3 — Install Dependencies

Add the MVP dependencies:

```bash
uv add streamlit python-dotenv pydantic pymupdf langchain langchain-openai langchain-community langgraph chromadb tiktoken
uv add --dev pytest
```

---

## 7. Step 4 — Configure Environment Variables

Create `.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHROMA_DIR=data/chroma
UPLOAD_DIR=data/uploads
```

Create your actual `.env` file:

```bash
cp .env.example .env
```

Then edit `.env` and add your real API key.

Create `.gitignore`:

```gitignore
.venv/
.env
__pycache__/
.pytest_cache/
data/uploads/
data/chroma/
*.pyc
```

---

## 8. Step 5 — Add Configuration

Create `src/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/uploads")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")
```

---

## 9. Step 6 — Define Shared Schemas

Create `src/schemas.py`:

```python
from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    text: str
    source: str
    chunk_id: str
    page: Optional[int] = None
    chunk_index: int


class RetrievedChunk(BaseModel):
    text: str
    source: str
    chunk_id: str
    page: Optional[int] = None
    score: Optional[float] = None


class AgentState(TypedDict):
    question: str
    rewritten_queries: List[str]
    retrieved_chunks: List[dict]
    evidence_sufficient: bool
    answer: str
    attempts: int
```

---

## 10. Step 7 — Build Document Ingestion

Create `src/ingestion.py`:

```python
from pathlib import Path
import fitz


def extract_text_from_pdf(file_path: str) -> list[dict]:
    pages = []
    doc = fitz.open(file_path)

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        if text.strip():
            pages.append({
                "text": text,
                "page": page_number,
                "source": Path(file_path).name,
            })

    return pages


def extract_text_from_plain_file(file_path: str) -> list[dict]:
    path = Path(file_path)
    text = path.read_text(encoding="utf-8", errors="ignore")

    if not text.strip():
        return []

    return [{
        "text": text,
        "page": None,
        "source": path.name,
    }]


def extract_document_text(file_path: str) -> list[dict]:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)

    if suffix in [".txt", ".md"]:
        return extract_text_from_plain_file(file_path)

    raise ValueError(f"Unsupported file type: {suffix}")
```

---

## 11. Step 8 — Build Text Chunking

Create `src/chunking.py`:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.schemas import DocumentChunk


def chunk_pages(pages: list[dict], chunk_size: int = 1000, chunk_overlap: int = 150) -> list[DocumentChunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[DocumentChunk] = []

    for page in pages:
        split_texts = splitter.split_text(page["text"])

        for index, text in enumerate(split_texts):
            chunk_id = f"{page['source']}::page-{page['page']}::chunk-{index}"
            chunks.append(
                DocumentChunk(
                    text=text,
                    source=page["source"],
                    page=page.get("page"),
                    chunk_index=index,
                    chunk_id=chunk_id,
                )
            )

    return chunks
```

Important: `RecursiveCharacterTextSplitter` may require this package depending on your LangChain version:

```bash
uv add langchain-text-splitters
```

If needed, add it to `pyproject.toml`.

---

## 12. Step 9 — Build the Vector Store

Create `src/vector_store.py`:

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from src.config import CHROMA_DIR, OPENAI_EMBEDDING_MODEL
from src.schemas import DocumentChunk


def get_embeddings():
    return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)


def get_vector_store():
    return Chroma(
        collection_name="agentic_rag_docs",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def add_chunks_to_vector_store(chunks: list[DocumentChunk]) -> int:
    vector_store = get_vector_store()

    documents = []
    ids = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk.text,
                metadata={
                    "source": chunk.source,
                    "page": chunk.page,
                    "chunk_index": chunk.chunk_index,
                    "chunk_id": chunk.chunk_id,
                },
            )
        )
        ids.append(chunk.chunk_id)

    if documents:
        vector_store.add_documents(documents=documents, ids=ids)

    return len(documents)
```

Install the Chroma integration package if needed:

```bash
uv add langchain-chroma
```

Then add it to `pyproject.toml`.

Your updated dependency list should include:

```txt
langchain-text-splitters
langchain-chroma
```

---

## 13. Step 10 — Build the Retriever Tool

Create `src/retriever.py`:

```python
from src.vector_store import get_vector_store


def search_documents(query: str, k: int = 5) -> list[dict]:
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_relevance_scores(query, k=k)

    chunks = []

    for doc, score in results:
        chunks.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source"),
            "page": doc.metadata.get("page"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "score": score,
        })

    return chunks
```

---

## 14. Step 11 — Create Prompts

Create `src/prompts.py`:

```python
PLANNER_PROMPT = """
You are a query planning assistant for a document question-answering system.

User question:
{question}

Create 1 to 4 search queries that would help retrieve evidence from the user's uploaded documents.
Return only the queries, one per line.
"""

EVIDENCE_EVALUATOR_PROMPT = """
You are checking whether retrieved document evidence is enough to answer a user question.

Question:
{question}

Retrieved evidence:
{evidence}

Answer with only one word:
SUFFICIENT or INSUFFICIENT
"""

ANSWER_PROMPT = """
You are a careful research assistant. Answer the user's question using only the provided evidence.

Rules:
- Use only the evidence below.
- If the evidence is not enough, say what is missing.
- Include citations like [source, page X] after supported claims.
- Do not invent facts.

Question:
{question}

Evidence:
{evidence}

Final answer:
"""

QUIZ_PROMPT = """
Create a short quiz using only the provided evidence.

Rules:
- Create 5 questions.
- Mix multiple-choice and short-answer questions.
- Include an answer key.
- Cite the source for each answer.

Topic or request:
{question}

Evidence:
{evidence}
"""
```

---

## 15. Step 12 — Build the Agentic Workflow with LangGraph

Create `src/agent.py`:

```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from src.config import OPENAI_MODEL
from src.schemas import AgentState
from src.retriever import search_documents
from src.prompts import PLANNER_PROMPT, EVIDENCE_EVALUATOR_PROMPT, ANSWER_PROMPT, QUIZ_PROMPT

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

MAX_ATTEMPTS = 2


def format_evidence(chunks: list[dict]) -> str:
    formatted = []

    for index, chunk in enumerate(chunks, start=1):
        page = chunk.get("page")
        page_text = f", page {page}" if page else ""
        formatted.append(
            f"[Evidence {index}] Source: {chunk.get('source')}{page_text}\n"
            f"Chunk ID: {chunk.get('chunk_id')}\n"
            f"Text: {chunk.get('text')}"
        )

    return "\n\n".join(formatted)


def plan_queries(state: AgentState) -> AgentState:
    prompt = PLANNER_PROMPT.format(question=state["question"])
    response = llm.invoke(prompt)

    queries = [line.strip("-• ").strip() for line in response.content.splitlines() if line.strip()]

    if not queries:
        queries = [state["question"]]

    state["rewritten_queries"] = queries[:4]
    return state


def retrieve_evidence(state: AgentState) -> AgentState:
    all_chunks = []
    seen_ids = set()

    for query in state["rewritten_queries"]:
        chunks = search_documents(query, k=4)

        for chunk in chunks:
            chunk_id = chunk.get("chunk_id")
            if chunk_id not in seen_ids:
                all_chunks.append(chunk)
                seen_ids.add(chunk_id)

    state["retrieved_chunks"] = all_chunks
    state["attempts"] = state.get("attempts", 0) + 1
    return state


def evaluate_evidence(state: AgentState) -> AgentState:
    evidence = format_evidence(state["retrieved_chunks"])
    prompt = EVIDENCE_EVALUATOR_PROMPT.format(
        question=state["question"],
        evidence=evidence,
    )
    response = llm.invoke(prompt)
    decision = response.content.strip().upper()

    state["evidence_sufficient"] = decision.startswith("SUFFICIENT")
    return state


def rewrite_queries_for_retry(state: AgentState) -> AgentState:
    retry_prompt = f"""
The first search did not find enough evidence.
Rewrite the user's question into 2 better document search queries.

User question: {state['question']}

Return only the rewritten queries, one per line.
"""
    response = llm.invoke(retry_prompt)
    queries = [line.strip("-• ").strip() for line in response.content.splitlines() if line.strip()]

    if not queries:
        queries = [state["question"]]

    state["rewritten_queries"] = queries[:2]
    return state


def generate_answer(state: AgentState) -> AgentState:
    evidence = format_evidence(state["retrieved_chunks"])

    if "quiz" in state["question"].lower():
        prompt = QUIZ_PROMPT.format(question=state["question"], evidence=evidence)
    else:
        prompt = ANSWER_PROMPT.format(question=state["question"], evidence=evidence)

    response = llm.invoke(prompt)
    state["answer"] = response.content
    return state


def decide_next_step(state: AgentState) -> str:
    if state["evidence_sufficient"]:
        return "generate_answer"

    if state["attempts"] >= MAX_ATTEMPTS:
        return "generate_answer"

    return "rewrite_queries_for_retry"


def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("plan_queries", plan_queries)
    graph.add_node("retrieve_evidence", retrieve_evidence)
    graph.add_node("evaluate_evidence", evaluate_evidence)
    graph.add_node("rewrite_queries_for_retry", rewrite_queries_for_retry)
    graph.add_node("generate_answer", generate_answer)

    graph.set_entry_point("plan_queries")
    graph.add_edge("plan_queries", "retrieve_evidence")
    graph.add_edge("retrieve_evidence", "evaluate_evidence")

    graph.add_conditional_edges(
        "evaluate_evidence",
        decide_next_step,
        {
            "generate_answer": "generate_answer",
            "rewrite_queries_for_retry": "rewrite_queries_for_retry",
        },
    )

    graph.add_edge("rewrite_queries_for_retry", "retrieve_evidence")
    graph.add_edge("generate_answer", END)

    return graph.compile()


agent_app = build_agent_graph()


def answer_question(question: str) -> dict:
    initial_state: AgentState = {
        "question": question,
        "rewritten_queries": [],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 0,
    }

    return agent_app.invoke(initial_state)
```

---

## 16. Step 13 — Build the Streamlit App

Create `app.py`:

```python
from pathlib import Path
import streamlit as st

from src.config import UPLOAD_DIR
from src.ingestion import extract_document_text
from src.chunking import chunk_pages
from src.vector_store import add_chunks_to_vector_store
from src.agent import answer_question

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Agentic RAG Copilot", page_icon="📚", layout="wide")

st.title("📚 Agentic RAG Research Copilot")
st.write("Upload documents, ask questions, and get cited answers grounded in your files.")

with st.sidebar:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, or Markdown files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    if st.button("Ingest Documents"):
        if not uploaded_files:
            st.warning("Please upload at least one file.")
        else:
            total_chunks = 0

            for uploaded_file in uploaded_files:
                save_path = Path(UPLOAD_DIR) / uploaded_file.name
                save_path.write_bytes(uploaded_file.getbuffer())

                try:
                    pages = extract_document_text(str(save_path))
                    chunks = chunk_pages(pages)
                    count = add_chunks_to_vector_store(chunks)
                    total_chunks += count
                    st.success(f"Ingested {uploaded_file.name}: {count} chunks")
                except Exception as error:
                    st.error(f"Failed to ingest {uploaded_file.name}: {error}")

            st.info(f"Total chunks added: {total_chunks}")

st.header("Ask a Question")

question = st.text_area(
    "Question",
    placeholder="Example: Compare innate and adaptive immunity and create a 5-question quiz.",
)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Running agentic retrieval workflow..."):
            result = answer_question(question)

        st.subheader("Answer")
        st.markdown(result["answer"])

        st.subheader("Agent Details")
        st.write(f"Evidence sufficient: `{result['evidence_sufficient']}`")
        st.write(f"Retrieval attempts: `{result['attempts']}`")

        with st.expander("Search queries used"):
            for query in result["rewritten_queries"]:
                st.write(f"- {query}")

        with st.expander("Retrieved evidence"):
            for index, chunk in enumerate(result["retrieved_chunks"], start=1):
                st.markdown(f"### Evidence {index}")
                st.write(f"Source: {chunk.get('source')}")
                st.write(f"Page: {chunk.get('page')}")
                st.write(f"Score: {chunk.get('score')}")
                st.write(chunk.get("text"))
```

---

## 17. Step 14 — Run the App

Run:

```bash
uv run streamlit run app.py
```

Then open the local URL shown in the terminal.

Typical URL:

```text
http://localhost:8501
```

---

## 18. Step 15 — Test the MVP Manually

Use a small PDF or Markdown file first.

Try questions like:

```text
Summarize this document in 5 bullet points.
```

```text
What are the main definitions in this document?
```

```text
Create a 5-question quiz from this document.
```

```text
What does this document say about photosynthesis?
```

Then test a question not answered by the document:

```text
What does this document say about quantum computing?
```

The system should say the document does not provide enough information.

---

## 19. Step 16 — Add Basic Tests

Create `tests/test_chunking.py`:

```python
from src.chunking import chunk_pages


def test_chunk_pages_returns_chunks():
    pages = [{
        "text": "This is a test document. " * 100,
        "page": 1,
        "source": "test.txt",
    }]

    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 0
    assert chunks[0].source == "test.txt"
    assert chunks[0].page == 1
```

Create `tests/test_ingestion.py`:

```python
from pathlib import Path
from src.ingestion import extract_text_from_plain_file


def test_extract_text_from_plain_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Hello world", encoding="utf-8")

    pages = extract_text_from_plain_file(str(file_path))

    assert len(pages) == 1
    assert pages[0]["text"] == "Hello world"
    assert pages[0]["source"] == "sample.txt"
```

Run tests:

```bash
uv run pytest
```

---

## 20. Step 17 — Add Better Citation Formatting

The MVP prompt asks the LLM to cite sources. For a stronger version, add citation labels before answer generation.

Update `format_evidence` in `src/agent.py` so each source has a stable citation ID:

```python
def format_evidence(chunks: list[dict]) -> str:
    formatted = []

    for index, chunk in enumerate(chunks, start=1):
        page = chunk.get("page")
        page_text = f", page {page}" if page else ""
        citation = f"[{index}] {chunk.get('source')}{page_text}"

        formatted.append(
            f"Citation: {citation}\n"
            f"Chunk ID: {chunk.get('chunk_id')}\n"
            f"Text: {chunk.get('text')}"
        )

    return "\n\n".join(formatted)
```

Then change the answer prompt rule:

```text
Use citation IDs exactly like [1], [2], or [3] after supported claims.
```

This makes citations easier to verify.

---

## 21. Step 18 — Add a Grounding Checker

Add this prompt to `src/prompts.py`:

```python
GROUNDING_CHECK_PROMPT = """
You are checking whether an answer is grounded in retrieved evidence.

Question:
{question}

Evidence:
{evidence}

Answer:
{answer}

Return:
- Grounded: Yes or No
- Unsupported claims: list any unsupported claims
- Suggested fix: explain how to make the answer safer
"""
```

Add this function to `src/agent.py`:

```python
from src.prompts import GROUNDING_CHECK_PROMPT


def check_grounding(question: str, chunks: list[dict], answer: str) -> str:
    evidence = format_evidence(chunks)
    prompt = GROUNDING_CHECK_PROMPT.format(
        question=question,
        evidence=evidence,
        answer=answer,
    )
    response = llm.invoke(prompt)
    return response.content
```

Then call it in the Streamlit app after `answer_question(question)`:

```python
grounding_report = check_grounding(
    question,
    result["retrieved_chunks"],
    result["answer"],
)

with st.expander("Grounding report"):
    st.markdown(grounding_report)
```

Also import it:

```python
from src.agent import answer_question, check_grounding
```

---

## 22. Step 19 — Add Duplicate File Protection

Create `src/utils.py`:

```python
import hashlib
from pathlib import Path


def file_hash(file_path: str) -> str:
    path = Path(file_path)
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(8192), b""):
            digest.update(block)

    return digest.hexdigest()
```

Simple MVP approach:

- Store hashes in a local text file.
- Before ingesting a file, check whether its hash already exists.

Add this to `src/utils.py`:

```python
HASH_LOG = "data/ingested_hashes.txt"


def already_ingested(hash_value: str) -> bool:
    path = Path(HASH_LOG)
    if not path.exists():
        return False

    return hash_value in path.read_text().splitlines()


def record_ingested(hash_value: str) -> None:
    path = Path(HASH_LOG)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(hash_value + "\n")
```

Then use it in `app.py` before ingestion:

```python
from src.utils import file_hash, already_ingested, record_ingested
```

Inside the upload loop:

```python
hash_value = file_hash(str(save_path))

if already_ingested(hash_value):
    st.warning(f"Skipping {uploaded_file.name}; already ingested.")
    continue

# after successful ingestion
record_ingested(hash_value)
```

---

## 23. Step 20 — Add FastAPI Backend, Optional

For a cleaner production-style architecture, you can add FastAPI.

Install:

```bash
uv add fastapi uvicorn python-multipart
```

Create `api.py`:

```python
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from src.config import UPLOAD_DIR
from src.ingestion import extract_document_text
from src.chunking import chunk_pages
from src.vector_store import add_chunks_to_vector_store
from src.agent import answer_question

app = FastAPI(title="Agentic RAG Copilot API")

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    save_path = Path(UPLOAD_DIR) / file.filename
    save_path.write_bytes(await file.read())

    pages = extract_document_text(str(save_path))
    chunks = chunk_pages(pages)
    count = add_chunks_to_vector_store(chunks)

    return {"filename": file.filename, "chunks_added": count}


@app.post("/ask")
def ask(request: QuestionRequest):
    return answer_question(request.question)
```

Run it:

```bash
uv run uvicorn api:app --reload
```

Open:

```text
http://localhost:8000/docs
```

---

## 24. Step 21 — Improve Retrieval Quality

After the MVP works, improve retrieval with these upgrades.

### 24.1 Increase Retrieved Chunks

In `search_documents`, try `k=8` instead of `k=5`.

### 24.2 Add Similarity Score Filtering

Example:

```python
MIN_SCORE = 0.35
chunks = [chunk for chunk in chunks if chunk["score"] is None or chunk["score"] >= MIN_SCORE]
```

Be careful: relevance score ranges can vary by vector store and embedding configuration.

### 24.3 Add Hybrid Search

Combine:

- Vector search
- Keyword search
- Reranking

A simple version can use BM25 with `rank-bm25`.

Install:

```bash
uv add rank-bm25
```

This is optional and usually not needed for the first MVP.

---

## 25. Step 22 — Improve the Agent

The first agent workflow is intentionally simple. Possible improvements:

### Add Query Classification

Classify questions as:

- Simple factual question
- Comparison question
- Summary request
- Quiz request
- Out-of-scope question

### Add Specialized Answer Modes

Use different prompts for:

- Summary
- Explanation
- Comparison table
- Quiz
- Study guide
- Flashcards

### Add Better Evidence Evaluation

Instead of only returning `SUFFICIENT` or `INSUFFICIENT`, return JSON:

```json
{
  "sufficient": true,
  "missing_information": [],
  "recommended_queries": []
}
```

This makes the agent easier to control.

---

## 26. Step 23 — Add Evaluation Dataset

Create a small folder:

```text
evaluation/
├── sample_docs/
└── questions.json
```

Example `questions.json`:

```json
[
  {
    "question": "What is innate immunity?",
    "expected_keywords": ["non-specific", "first line", "rapid"],
    "source": "immunity_notes.pdf"
  }
]
```

Create an evaluation script later that checks:

- Whether the answer includes expected keywords.
- Whether citations are present.
- Whether the correct source was retrieved.
- Whether unsupported questions are refused.

---

## 27. Step 24 — Deployment Options

### Option A: Streamlit Community Cloud

Good for demos.

Steps:

1. Push the project to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from your repository.
4. Add `OPENAI_API_KEY` in app secrets.
5. Deploy.

Note: persistent local Chroma storage may be limited depending on hosting settings.

### Option B: Render

Good for FastAPI backend.

Steps:

1. Push project to GitHub.
2. Create a new Web Service on Render.
3. Add environment variables.
4. Use start command:

```bash
uvicorn api:app --host 0.0.0.0 --port $PORT
```

### Option C: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t agentic-rag-copilot .
docker run -p 8501:8501 --env-file .env agentic-rag-copilot
```

---

## 28. Step 25 — Common Errors and Fixes

### Error: `OPENAI_API_KEY is missing`

Fix:

- Make sure `.env` exists.
- Make sure the key is named exactly `OPENAI_API_KEY`.
- Restart the app after editing `.env`.

### Error: `ModuleNotFoundError: langchain_chroma`

Fix:

```bash
uv add langchain-chroma
```

Add this to `pyproject.toml`:

```txt
langchain-chroma
```

### Error: `ModuleNotFoundError: langchain_text_splitters`

Fix:

```bash
uv add langchain-text-splitters
```

Add this to `pyproject.toml`:

```txt
langchain-text-splitters
```

### Error: PDF uploads but no useful text appears

Possible cause:

- The PDF is scanned and contains images, not selectable text.

Fix:

- Add OCR support later with Tesseract or a document OCR service.

### Error: Answers are hallucinated

Fixes:

- Strengthen the answer prompt.
- Lower LLM temperature to `0`.
- Add a grounding checker.
- Make the system say “not enough evidence” when citations are weak.

### Error: Retrieval gets irrelevant chunks

Fixes:

- Use smaller chunk size.
- Increase overlap.
- Retrieve more chunks.
- Add reranking.
- Use hybrid keyword + vector search.

---

## 29. Step 26 — Suggested Development Timeline

### Day 1

- Project setup
- Environment variables
- File upload
- PDF/TXT/Markdown text extraction

### Day 2

- Chunking
- Embeddings
- ChromaDB storage
- Basic retriever

### Day 3

- Basic RAG answer generation
- Streamlit UI
- Citation display

### Day 4

- LangGraph workflow
- Query planning
- Evidence evaluation
- Retry retrieval

### Day 5

- Quiz generation
- Evidence panel
- Grounding checker
- Tests and cleanup

---

## 30. Final Checklist

Before calling the project complete, verify:

- [ ] App starts with `uv run streamlit run app.py`.
- [ ] User can upload a PDF.
- [ ] User can upload TXT or Markdown files.
- [ ] Text is chunked correctly.
- [ ] Chunks are stored in ChromaDB.
- [ ] User can ask a question.
- [ ] Agent creates search queries.
- [ ] Agent retrieves evidence.
- [ ] Agent evaluates evidence sufficiency.
- [ ] Agent retries retrieval when needed.
- [ ] Final answer includes citations.
- [ ] App shows retrieved evidence.
- [ ] App handles unsupported questions safely.
- [ ] Tests pass with `uv run pytest`.

---

## 31. Recommended Next Enhancements

Once the MVP works, add:

- Login and user-specific document spaces.
- Document deletion.
- OCR for scanned PDFs.
- Better citation mapping.
- Reranking.
- Hybrid search.
- FastAPI backend.
- Docker deployment.
- Evaluation dashboard.
- Export answers and quizzes to Markdown or PDF.
