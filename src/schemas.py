from pydantic import BaseModel, Field

# Raw text extracted from a source file before we split it into chunks.
class ExtractedPage(BaseModel):
    text: str = Field(min_length=1)
    source: str
    page: int | None = None


# A searchable chunk that is ready to be embedded and stored.
class DocumentChunk(BaseModel):
    chunk_id: str
    text: str = Field(min_length=1)
    source: str
    page: int | None = None
    chunk_index: int = Field(ge=0)


# A retrieved chunk plus optional search metadata like relevance score.
class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str = Field(min_length=1)
    source: str
    page: int | None = None
    score: float | None = None
