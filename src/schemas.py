from typing import TypedDict

from pydantic import BaseModel, Field, model_validator

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


class GroundingCheckResult(BaseModel):
    grounded: bool
    unsupported_claims: list[str]
    suggested_fix: str = ""

    @model_validator(mode="after")
    def validate_suggested_fix(self) -> "GroundingCheckResult":
        has_fix = bool(self.suggested_fix.strip())
        if not self.grounded and not has_fix:
            raise ValueError("suggested_fix is required when grounded is False")
        return self


# Shared state that flows through the LangGraph agent workflow.
class AgentState(TypedDict):
    question: str
    rewritten_queries: list[str]
    retrieved_chunks: list[RetrievedChunk]
    evidence_sufficient: bool
    answer: str
    attempts: int
    grounding_report: GroundingCheckResult | None
