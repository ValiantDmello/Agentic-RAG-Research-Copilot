# Agentic RAG Research Copilot — Software Requirements Specification

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for an **Agentic Retrieval-Augmented Generation (RAG) Research Copilot**. The system allows users to upload documents and ask questions about them. Unlike basic RAG systems, this project uses an agentic workflow that can plan, retrieve evidence, evaluate whether the evidence is sufficient, perform follow-up retrieval, and generate cited answers.

### 1.2 Scope
The system will support document-based question answering for a focused knowledge base such as lecture notes, textbooks, research papers, company policies, or technical documentation.

The application will:

- Ingest user-uploaded documents.
- Split documents into searchable chunks.
- Store document embeddings in a vector database.
- Accept natural language questions.
- Plan retrieval steps for complex questions.
- Retrieve relevant evidence.
- Evaluate whether retrieved evidence is enough.
- Generate grounded answers with citations.
- Optionally generate quizzes or summaries from retrieved content.

### 1.3 Intended Users
The intended users include:

- Students reviewing class notes.
- Researchers analyzing papers.
- Employees searching internal documentation.
- Developers searching technical docs.
- Teachers preparing study material.

### 1.4 Definitions

| Term | Meaning |
|---|---|
| RAG | Retrieval-Augmented Generation, a technique where an LLM uses retrieved documents to answer questions. |
| Agentic RAG | A RAG system with planning, tool use, iterative retrieval, and self-checking. |
| Chunk | A smaller section of a document used for retrieval. |
| Embedding | A numerical representation of text used for semantic search. |
| Vector Database | A database optimized for storing and searching embeddings. |
| Citation | A reference to the document and section used to support an answer. |
| Grounding | Ensuring the answer is supported by source documents. |

---

## 2. Overall Description

### 2.1 Product Perspective
The project is a web-based AI assistant with a backend pipeline for document ingestion, vector search, agent orchestration, and answer generation.

A typical user flow is:

1. User uploads documents.
2. System extracts text.
3. System chunks text and creates embeddings.
4. User asks a question.
5. Agent analyzes the question and creates a retrieval plan.
6. Retriever searches the vector database.
7. Agent checks if retrieved evidence is sufficient.
8. If needed, agent performs more searches.
9. System generates a final answer with citations.

### 2.2 Product Functions
The main product functions are:

- Document upload.
- Text extraction from PDFs, DOCX, TXT, and Markdown.
- Chunking and metadata storage.
- Embedding generation.
- Vector search.
- Query planning.
- Multi-step retrieval.
- Evidence evaluation.
- Cited answer generation.
- Quiz generation.
- Conversation history support.
- Basic admin/debug view for retrieved chunks.

### 2.3 User Classes

| User Class | Description |
|---|---|
| Student | Uploads notes and asks study questions. |
| Teacher | Uploads material and generates summaries or quizzes. |
| Knowledge Worker | Searches company/internal documents. |
| Developer | Searches project or API documentation. |
| Admin | Manages documents, debugging, and system settings. |

### 2.4 Operating Environment
The MVP should run locally and optionally be deployable to the cloud.

Recommended environment:

- Python 3.11+
- Streamlit frontend
- FastAPI backend, optional for larger version
- LangGraph for agent workflow
- LangChain or LlamaIndex for document processing utilities
- ChromaDB or FAISS for vector search
- OpenAI API or a local LLM provider
- SQLite or PostgreSQL for metadata

### 2.5 Assumptions and Dependencies

- Users provide documents they are allowed to use.
- The LLM provider is available and configured correctly.
- Uploaded documents contain extractable text.
- For scanned PDFs, OCR may be needed in a later version.
- The initial MVP focuses on English text.

---

## 3. System Features and Requirements

## 3.1 Document Upload and Ingestion

### Description
Users should be able to upload documents into the system. The system extracts text and prepares it for retrieval.

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | The system shall allow users to upload PDF files. | Must |
| FR-002 | The system shall allow users to upload TXT and Markdown files. | Must |
| FR-003 | The system should allow users to upload DOCX files. | Should |
| FR-004 | The system shall extract text from uploaded documents. | Must |
| FR-005 | The system shall store document metadata such as filename, upload time, and file type. | Must |
| FR-006 | The system should display ingestion status to the user. | Should |
| FR-007 | The system shall handle failed uploads gracefully. | Must |

### Acceptance Criteria

- A user can upload at least one PDF and ask questions about it.
- The system confirms successful ingestion.
- The system does not crash when unsupported or corrupted files are uploaded.

---

## 3.2 Text Chunking

### Description
The extracted text should be split into chunks suitable for semantic search.

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-008 | The system shall split documents into chunks. | Must |
| FR-009 | The system shall preserve metadata for each chunk. | Must |
| FR-010 | The system should use overlapping chunks to avoid losing context. | Should |
| FR-011 | The system should allow chunk size and overlap configuration. | Could |

### Recommended Defaults

- Chunk size: 800–1,200 tokens or characters depending on implementation.
- Chunk overlap: 100–200 tokens or characters.
- Metadata: source file, page number if available, chunk index.

### Acceptance Criteria

- Each document produces multiple searchable chunks.
- Each retrieved chunk can be traced back to its source document.

---

## 3.3 Embedding and Vector Storage

### Description
Chunks should be converted into embeddings and stored in a vector database.

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-012 | The system shall generate embeddings for each chunk. | Must |
| FR-013 | The system shall store embeddings in a vector database. | Must |
| FR-014 | The system shall store chunk text and metadata with each vector. | Must |
| FR-015 | The system should avoid duplicate ingestion of the same file. | Should |
| FR-016 | The system should support deleting a document and its chunks. | Could |

### Acceptance Criteria

- Uploaded document chunks are searchable by semantic similarity.
- Search results include source metadata.

---

## 3.4 Question Answering

### Description
Users should ask natural language questions and receive answers grounded in the uploaded documents.

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-017 | The system shall accept natural language questions. | Must |
| FR-018 | The system shall retrieve relevant chunks from the vector database. | Must |
| FR-019 | The system shall generate an answer using retrieved context. | Must |
| FR-020 | The system shall include citations in the final answer. | Must |
| FR-021 | The system shall say when the answer is not available in the documents. | Must |
| FR-022 | The system should support follow-up questions. | Should |

### Acceptance Criteria

- Answers include references to source documents.
- The system refuses to invent answers when no supporting evidence exists.

---

## 3.5 Agentic Query Planning

### Description
For complex questions, the system should break the user query into smaller search tasks.

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-023 | The system shall classify whether a question is simple or complex. | Should |
| FR-024 | The system shall create sub-questions for complex queries. | Should |
| FR-025 | The system shall retrieve evidence for each sub-question. | Should |
| FR-026 | The system shall combine evidence from multiple retrieval steps. | Should |

### Example
User question:

> Compare innate and adaptive immunity and create a quiz.

Possible sub-questions:

1. What is innate immunity?
2. What is adaptive immunity?
3. What are the differences between them?
4. What quiz questions can be generated from the evidence?

### Acceptance Criteria

- Complex questions produce better results than single-step retrieval.
- The agent can explain which sources were used.

---

## 3.6 Evidence Evaluation

### Description
The agent should judge whether retrieved evidence is enough to answer the question.

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-027 | The system shall evaluate whether retrieved chunks answer the question. | Must |
| FR-028 | The system shall perform another retrieval attempt if evidence is insufficient. | Should |
| FR-029 | The system shall limit the number of retrieval attempts. | Must |
| FR-030 | The system shall report uncertainty when evidence is weak. | Must |

### Acceptance Criteria

- The system does not loop forever.
- The final answer clearly identifies unsupported or uncertain claims.

---

## 3.7 Citation and Grounding Checker

### Description
The final answer should be checked against retrieved sources.

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-031 | The system shall attach citations to answer paragraphs or bullet points. | Must |
| FR-032 | The system shall check whether each major answer claim is supported by retrieved evidence. | Should |
| FR-033 | The system shall warn the user if an answer contains weakly supported claims. | Should |
| FR-034 | The system shall show source snippets in a debug/evidence panel. | Could |

### Acceptance Criteria

- A user can see which uploaded document supports each answer.
- Unsupported claims are reduced or flagged.

---

## 3.8 Quiz and Study Mode

### Description
The system should generate quizzes based only on uploaded material.

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-035 | The system should generate multiple-choice questions from retrieved content. | Should |
| FR-036 | The system should generate short-answer questions. | Should |
| FR-037 | The system should provide answer keys. | Should |
| FR-038 | The system should cite the source material for quiz answers. | Should |

### Acceptance Criteria

- Generated quiz questions are based on uploaded documents.
- Answer keys are supported by citations.

---

## 3.9 User Interface

### Description
The MVP user interface should be simple and usable.

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-039 | The system shall provide a document upload area. | Must |
| FR-040 | The system shall provide a chat input area. | Must |
| FR-041 | The system shall display final answers clearly. | Must |
| FR-042 | The system shall display citations. | Must |
| FR-043 | The system should display retrieved evidence in an expandable panel. | Should |
| FR-044 | The system should display ingestion and retrieval logs for debugging. | Could |

### Acceptance Criteria

- A user can upload a file and ask a question without using the command line.
- Citations and retrieved snippets are visible.

---

## 4. Non-Functional Requirements

## 4.1 Performance

| ID | Requirement | Priority |
|---|---|---|
| NFR-001 | The system should answer typical questions within 5–15 seconds. | Should |
| NFR-002 | The system shall support at least 100 uploaded documents in local MVP testing. | Should |
| NFR-003 | The system should retrieve relevant chunks in under 2 seconds for small collections. | Should |

## 4.2 Reliability

| ID | Requirement | Priority |
|---|---|---|
| NFR-004 | The system shall handle LLM API failures gracefully. | Must |
| NFR-005 | The system shall not lose already ingested documents after restart. | Must |
| NFR-006 | The system should log errors for debugging. | Should |

## 4.3 Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| NFR-007 | The system shall not expose uploaded documents to other users. | Must |
| NFR-008 | API keys shall be stored in environment variables. | Must |
| NFR-009 | The system should validate file types before ingestion. | Should |
| NFR-010 | The system should limit maximum upload file size. | Should |

## 4.4 Usability

| ID | Requirement | Priority |
|---|---|---|
| NFR-011 | The interface shall be understandable to non-technical users. | Must |
| NFR-012 | Error messages shall be clear and actionable. | Should |
| NFR-013 | Citations shall be easy to inspect. | Should |

## 4.5 Maintainability

| ID | Requirement | Priority |
|---|---|---|
| NFR-014 | The project shall use a modular folder structure. | Must |
| NFR-015 | The code should separate ingestion, retrieval, agent workflow, and UI logic. | Must |
| NFR-016 | The project should include tests for major modules. | Should |

---

## 5. System Architecture

## 5.1 High-Level Architecture

```text
User Interface
    |
    v
Application Controller
    |
    +--> Document Ingestion Pipeline
    |       |
    |       +--> Text Extraction
    |       +--> Chunking
    |       +--> Embedding
    |       +--> Vector Store
    |
    +--> Agentic RAG Workflow
            |
            +--> Query Classifier
            +--> Planner
            +--> Retriever Tool
            +--> Evidence Evaluator
            +--> Answer Generator
            +--> Grounding Checker
```

## 5.2 Agent Workflow

```text
User Question
    |
    v
Classify Question
    |
    v
Create Retrieval Plan
    |
    v
Search Documents
    |
    v
Evaluate Evidence
    |
    +--> If insufficient: rewrite query and search again
    |
    v
Generate Answer
    |
    v
Check Grounding
    |
    v
Return Answer with Citations
```

## 5.3 Main Components

| Component | Responsibility |
|---|---|
| UI Layer | Upload documents, ask questions, display answers. |
| Ingestion Service | Extract text, chunk documents, generate embeddings. |
| Vector Store Service | Store and retrieve document chunks. |
| Agent Orchestrator | Manage the multi-step agent workflow. |
| Retriever Tool | Perform semantic search over chunks. |
| Evidence Evaluator | Decide whether retrieved chunks are enough. |
| Answer Generator | Generate final answer using only retrieved evidence. |
| Citation Formatter | Format document references in the answer. |
| Grounding Checker | Detect unsupported claims. |

---

## 6. Data Requirements

## 6.1 Document Metadata

Each uploaded document should store:

- Document ID
- Filename
- File type
- Upload timestamp
- Number of chunks
- Source path
- Hash of file contents, optional

## 6.2 Chunk Metadata

Each chunk should store:

- Chunk ID
- Document ID
- Filename
- Page number if available
- Chunk index
- Chunk text
- Embedding vector

## 6.3 Conversation Data

Each chat turn may store:

- User question
- Retrieval queries used
- Retrieved chunks
- Final answer
- Citations
- Timestamp

---

## 7. External Interface Requirements

## 7.1 User Interface

The UI should include:

- File uploader
- Ingestion status messages
- Chat input
- Answer display
- Citation display
- Expandable evidence panel
- Optional settings sidebar

## 7.2 API Interface

For a FastAPI version, recommended endpoints are:

| Endpoint | Method | Purpose |
|---|---|---|
| `/upload` | POST | Upload and ingest files. |
| `/ask` | POST | Ask a question. |
| `/documents` | GET | List uploaded documents. |
| `/documents/{id}` | DELETE | Delete a document. |
| `/health` | GET | Check service status. |

## 7.3 LLM Provider Interface

The system should use an LLM for:

- Query planning
- Evidence evaluation
- Answer generation
- Grounding review
- Quiz generation

The LLM key must be stored in an `.env` file or deployment secret manager.

---

## 8. Error Handling

The system should handle:

- Unsupported file type
- Empty document text
- Embedding API failure
- LLM API failure
- Vector database unavailable
- No relevant chunks found
- User asks question outside uploaded documents

Expected behavior:

- Show a clear error message.
- Do not crash.
- Do not produce unsupported answers.

---

## 9. Testing Requirements

## 9.1 Unit Tests

Test the following modules:

- Text extraction
- Chunking
- Embedding wrapper
- Retriever
- Citation formatter
- Evidence evaluator output parser

## 9.2 Integration Tests

Test complete workflows:

- Upload document and ask a simple question.
- Ask a complex question requiring multiple retrievals.
- Ask a question not answered by documents.
- Generate a quiz from uploaded content.

## 9.3 Evaluation Tests

Use a small benchmark dataset with known answers.

Metrics:

- Retrieval precision
- Citation correctness
- Answer faithfulness
- Refusal correctness when answer is unavailable
- Latency

---

## 10. MVP Requirements

The MVP should include:

- Streamlit UI
- PDF/TXT/Markdown upload
- Text chunking
- ChromaDB vector store
- OpenAI embeddings
- LangGraph agent workflow
- Retrieval planning
- Evidence sufficiency check
- Cited answer generation
- Evidence panel

The MVP may exclude:

- User authentication
- Multi-user document isolation
- Production deployment
- Advanced OCR
- Full admin dashboard

---

## 11. Future Enhancements

Possible future improvements:

- User accounts and private workspaces
- OCR for scanned PDFs
- Hybrid search using vector + keyword search
- Reranking with a cross-encoder or LLM reranker
- Support for images, tables, and charts
- Document deletion and re-indexing
- Team knowledge base support
- Browser extension for saving web pages
- Automated flashcards
- Export answers to PDF or Markdown
- Evaluation dashboard
- Role-based access control

---

## 12. Success Criteria

The project is successful when:

- Users can upload documents and ask questions about them.
- Answers are grounded in retrieved source material.
- Citations are shown clearly.
- The agent can perform more than one retrieval step when needed.
- The system admits when uploaded documents do not contain enough information.
- The codebase is modular and understandable.
