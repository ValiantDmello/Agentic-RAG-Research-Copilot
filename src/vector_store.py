from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.config import CHROMA_DIR, OPENAI_EMBEDDING_MODEL
from src.schemas import DocumentChunk


def get_embeddings() -> OpenAIEmbeddings:
    """Create the embedding client used for vector indexing and search."""
    return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)


def get_vector_store() -> Chroma:
    """Open the persistent Chroma collection for document chunks."""
    return Chroma(
        collection_name="agentic_rag_docs",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def add_chunks_to_vector_store(chunks: list[DocumentChunk]) -> int:
    """Embed and store document chunks, returning how many were indexed."""
    vector_store = get_vector_store()
    documents: list[Document] = []
    ids: list[str] = []

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
