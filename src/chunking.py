from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.schemas import DocumentChunk, ExtractedPage


def chunk_pages(
    pages: list[ExtractedPage],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[DocumentChunk]:
    """Split extracted pages into overlapping chunks for semantic retrieval."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[DocumentChunk] = []

    for page in pages:
        split_texts = splitter.split_text(page.text)

        for index, text in enumerate(split_texts):
            chunk_id = f"{page.source}::page-{page.page}::chunk-{index}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=text,
                    source=page.source,
                    page=page.page,
                    chunk_index=index,
                )
            )

    return chunks
