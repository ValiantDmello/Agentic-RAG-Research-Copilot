"""LangGraph workflow skeleton for the agentic RAG pipeline."""

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from src.config import OPENAI_MODEL
from src.prompts import (
    ANSWER_PROMPT,
    EVIDENCE_EVALUATOR_PROMPT,
    PLANNER_PROMPT,
    QUIZ_PROMPT,
)
from src.retriever import search_documents
from src.schemas import AgentState, RetrievedChunk

# One shared model powers planning, evidence evaluation, retries, and answer generation.
# Temperature stays at 0 because this project values reliability over creativity.
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)


class QueryPlan(BaseModel):
    """Structured planner output so queries are not parsed from free text."""

    queries: list[str] = Field(
        min_length=1,
        max_length=4,
        description="One to four retrieval-focused search queries.",
    )


planner_llm = llm.with_structured_output(QueryPlan)

MAX_ATTEMPTS = 2


def format_evidence(chunks: list[RetrievedChunk]) -> str:
    """Convert retrieved chunks into a prompt-friendly evidence block."""
    formatted_chunks: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        page_text = f", page {chunk.page}" if chunk.page is not None else ""
        formatted_chunks.append(
            "\n".join(
                [
                    f"[Evidence {index}] Source: {chunk.source}{page_text}",
                    f"Chunk ID: {chunk.chunk_id}",
                    f"Text: {chunk.text}",
                ]
            )
        )

    return "\n\n".join(formatted_chunks)


def plan_queries(state: AgentState) -> AgentState:
    """Generate retrieval-friendly queries from the user question."""
    prompt = PLANNER_PROMPT.format(question=state["question"])
    response = planner_llm.invoke(prompt)
    queries = [query.strip() for query in response.queries if query.strip()]

    updated_state = state.copy()
    updated_state["rewritten_queries"] = queries[:4] if queries else [state["question"]]
    return updated_state


def retrieve_evidence(state: AgentState) -> AgentState:
    """Search the vector store for each planned query and collect evidence."""
    raise NotImplementedError("TODO 6: implement retrieve_evidence()")


def evaluate_evidence(state: AgentState) -> AgentState:
    """Decide whether the retrieved evidence is sufficient to answer safely."""
    raise NotImplementedError("TODO 7: implement evaluate_evidence()")


def rewrite_queries_for_retry(state: AgentState) -> AgentState:
    """Rewrite queries for a second retrieval attempt when evidence is weak."""
    raise NotImplementedError("TODO 8: implement rewrite_queries_for_retry()")


def generate_answer(state: AgentState) -> AgentState:
    """Create the final grounded answer or quiz from retrieved evidence."""
    raise NotImplementedError("TODO 9: implement generate_answer()")


def decide_next_step(state: AgentState) -> str:
    """Choose whether to retry retrieval or finish with answer generation."""
    raise NotImplementedError("TODO 10: implement decide_next_step()")


def build_agent_graph():
    """Create and compile the LangGraph workflow for the RAG agent."""
    raise NotImplementedError("TODO 11: implement build_agent_graph()")


def answer_question(question: str) -> dict:
    """Run the agent workflow for a single user question."""
    raise NotImplementedError("TODO 13: implement answer_question()")
