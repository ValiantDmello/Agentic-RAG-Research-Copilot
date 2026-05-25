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
    RETRY_QUERY_PROMPT,
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


class RetryQueryPlan(BaseModel):
    """Structured retry-planner output for a second retrieval attempt."""

    queries: list[str] = Field(
        min_length=1,
        max_length=2,
        description="One or two improved retrieval queries for a retry attempt.",
    )


class EvidenceEvaluation(BaseModel):
    """Structured evaluator output for evidence sufficiency decisions."""

    sufficient: bool = Field(
        description="Whether the retrieved evidence is sufficient to answer safely.",
    )


planner_llm = llm.with_structured_output(QueryPlan)
retry_planner_llm = llm.with_structured_output(RetryQueryPlan)
evaluator_llm = llm.with_structured_output(EvidenceEvaluation)

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
    """Search the vector store for each planned query and accumulate unique evidence."""
    all_chunks = list(state["retrieved_chunks"])
    seen_chunk_ids = {chunk.chunk_id for chunk in all_chunks}

    for query in state["rewritten_queries"]:
        chunks = search_documents(query, k=4)

        for chunk in chunks:
            if chunk.chunk_id in seen_chunk_ids:
                continue

            all_chunks.append(chunk)
            seen_chunk_ids.add(chunk.chunk_id)

    updated_state = state.copy()
    updated_state["retrieved_chunks"] = all_chunks
    updated_state["attempts"] = state["attempts"] + 1
    return updated_state


def evaluate_evidence(state: AgentState) -> AgentState:
    """Decide whether the retrieved evidence is sufficient to answer safely."""
    evidence = format_evidence(state["retrieved_chunks"])
    prompt = EVIDENCE_EVALUATOR_PROMPT.format(
        question=state["question"],
        evidence=evidence,
    )
    response = evaluator_llm.invoke(prompt)

    updated_state = state.copy()
    updated_state["evidence_sufficient"] = response.sufficient
    return updated_state


def rewrite_queries_for_retry(state: AgentState) -> AgentState:
    """Rewrite queries for a second retrieval attempt when evidence is weak."""
    evidence = format_evidence(state["retrieved_chunks"])
    prior_queries = "\n".join(f"- {query}" for query in state["rewritten_queries"])
    # With the current AgentState, retries only remember the latest query set.
    # If we allow more than one retry later, add query history to state so a
    # third attempt can also avoid repeating the first attempt's queries.
    prompt = RETRY_QUERY_PROMPT.format(
        question=state["question"],
        previous_queries=prior_queries or "- None",
        evidence=evidence or "No evidence retrieved.",
    )
    response = retry_planner_llm.invoke(prompt)
    queries = [query.strip() for query in response.queries if query.strip()]

    updated_state = state.copy()
    updated_state["rewritten_queries"] = queries[:2] if queries else [state["question"]]
    return updated_state


def generate_answer(state: AgentState) -> AgentState:
    """Create the final grounded answer or quiz from retrieved evidence."""
    evidence = format_evidence(state["retrieved_chunks"])

    if "quiz" in state["question"].lower():
        prompt = QUIZ_PROMPT.format(
            question=state["question"],
            evidence=evidence,
        )
    else:
        prompt = ANSWER_PROMPT.format(
            question=state["question"],
            evidence=evidence,
        )

    response = llm.invoke(prompt)
    response_text = response.content if isinstance(response.content, str) else str(response.content)

    updated_state = state.copy()
    updated_state["answer"] = response_text
    return updated_state


def decide_next_step(state: AgentState) -> str:
    """Choose whether to retry retrieval or finish with answer generation."""
    raise NotImplementedError("TODO 10: implement decide_next_step()")


def build_agent_graph():
    """Create and compile the LangGraph workflow for the RAG agent."""
    raise NotImplementedError("TODO 11: implement build_agent_graph()")


def answer_question(question: str) -> dict:
    """Run the agent workflow for a single user question."""
    raise NotImplementedError("TODO 13: implement answer_question()")
