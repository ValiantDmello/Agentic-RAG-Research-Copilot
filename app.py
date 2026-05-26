from pathlib import Path

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from src.agent import answer_question
from src.chunking import chunk_pages
from src.config import UPLOAD_DIR
from src.ingestion import extract_document_text
from src.vector_store import add_chunks_to_vector_store

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def _ensure_session_state() -> None:
    """Initialize the Streamlit state used to persist UI results across reruns."""
    if "ingestion_messages" not in st.session_state:
        st.session_state.ingestion_messages = []

    if "latest_result" not in st.session_state:
        st.session_state.latest_result = None

    if "latest_question" not in st.session_state:
        st.session_state.latest_question = ""


def _ingest_uploaded_files(uploaded_files: list[UploadedFile]) -> None:
    """Save uploaded files, ingest them, and record per-file feedback."""
    if not uploaded_files:
        st.session_state.ingestion_messages = [
            ("warning", "Please upload at least one file."),
        ]
        return

    messages: list[tuple[str, str]] = []
    total_chunks = 0

    for uploaded_file in uploaded_files:
        save_path = Path(UPLOAD_DIR) / uploaded_file.name
        save_path.write_bytes(uploaded_file.getbuffer())

        try:
            pages = extract_document_text(str(save_path))
            chunks = chunk_pages(pages)
            chunk_count = add_chunks_to_vector_store(chunks)
            total_chunks += chunk_count
            messages.append(
                ("success", f"Ingested {uploaded_file.name}: {chunk_count} chunks")
            )
        except Exception as error:
            messages.append(
                ("error", f"Failed to ingest {uploaded_file.name}: {error}")
            )

    messages.append(("info", f"Total chunks added: {total_chunks}"))
    st.session_state.ingestion_messages = messages


def _display_ingestion_messages() -> None:
    """Render persisted ingestion feedback in the sidebar."""
    for level, message in st.session_state.ingestion_messages:
        getattr(st, level)(message)


def _run_question(question: str) -> None:
    """Execute the LangGraph workflow and persist the result."""
    clean_question = question.strip()

    if not clean_question:
        st.warning("Please enter a question.")
        return

    with st.spinner("Running agentic retrieval workflow..."):
        st.session_state.latest_result = answer_question(clean_question)
        st.session_state.latest_question = clean_question


def _render_result() -> None:
    """Show the latest answer plus workflow details and retrieved evidence."""
    result = st.session_state.latest_result
    if not result:
        return
    grounding_report = result.get("grounding_report")

    st.subheader("Answer")
    st.markdown(result["answer"])

    if grounding_report is not None:
        st.subheader("Grounding Check")
        if grounding_report.grounded:
            st.success("The answer appears grounded in the retrieved evidence.")
        else:
            st.warning("The answer may include claims not fully supported by the evidence.")

        st.write(f"Grounded: `{grounding_report.grounded}`")

        if grounding_report.unsupported_claims:
            st.write("Unsupported claims:")
            for claim in grounding_report.unsupported_claims:
                st.write(f"- {claim}")
        else:
            st.write("Unsupported claims: none identified.")

        st.write("Suggested fix:")
        st.write(grounding_report.suggested_fix)

    st.subheader("Agent Details")
    st.write(f"Question: `{st.session_state.latest_question}`")
    st.write(f"Evidence sufficient: `{result['evidence_sufficient']}`")
    st.write(f"Retrieval attempts: `{result['attempts']}`")

    with st.expander("Search queries used", expanded=False):
        for query in result["rewritten_queries"]:
            st.write(f"- {query}")

    with st.expander("Retrieved evidence", expanded=False):
        if not result["retrieved_chunks"]:
            st.info("No evidence chunks were retrieved.")
            return

        for index, chunk in enumerate(result["retrieved_chunks"], start=1):
            st.markdown(f"### Evidence {index}")
            st.write(f"Source: {chunk.source}")
            st.write(f"Page: {chunk.page}")
            st.write(f"Score: {chunk.score}")
            st.write(chunk.text)


def main() -> None:
    """Run the Streamlit app for document ingestion and grounded Q&A."""
    st.set_page_config(
        page_title="Agentic RAG Copilot",
        page_icon=":books:",
        layout="wide",
    )
    _ensure_session_state()

    st.title("Agentic RAG Research Copilot")
    st.write(
        "Upload documents, ask questions, and get cited answers grounded in your files."
    )

    with st.sidebar:
        st.header("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF, TXT, or Markdown files",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
        )

        if st.button("Ingest Documents", use_container_width=True):
            _ingest_uploaded_files(uploaded_files)

        _display_ingestion_messages()

    st.header("Ask a Question")
    question = st.text_area(
        "Question",
        placeholder=(
            "Example: Compare innate and adaptive immunity and create a 5-question quiz."
        ),
        height=120,
    )

    if st.button("Ask", type="primary"):
        _run_question(question)

    _render_result()


if __name__ == "__main__":
    main()
