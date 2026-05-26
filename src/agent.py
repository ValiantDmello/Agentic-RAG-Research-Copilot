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


def _log_node(name: str) -> None:
    """Print the current graph node for learning and debugging."""
    print(f"\n[Agent Node] {name}")


def _log_queries(label: str, queries: list[str]) -> None:
    """Print search queries in a compact numbered list."""
    print(label)
    if not queries:
        print("  (none)")
        return

    for index, query in enumerate(queries, start=1):
        print(f"  {index}. {query}")


def _log_retrieved_chunks(chunks: list[RetrievedChunk]) -> None:
    """Print retrieved chunk metadata so retrieval behavior is easy to inspect."""
    print(f"Retrieved chunks: {len(chunks)}")
    if not chunks:
        print("  (none)")
        return

    for index, chunk in enumerate(chunks, start=1):
        page_text = f", page {chunk.page}" if chunk.page is not None else ""
        print(
            f"  {index}. {chunk.source}{page_text} | "
            f"{chunk.chunk_id} | score={chunk.score}"
        )


def format_evidence(chunks: list[RetrievedChunk]) -> str:
    """Convert retrieved chunks into a prompt-friendly evidence block."""
    formatted_chunks: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        page_text = f", page {chunk.page}" if chunk.page is not None else ""
        formatted_chunks.append(
            "\n".join(
                [
                    f"Citation: [{index}] {chunk.source}{page_text}",
                    f"Chunk ID: {chunk.chunk_id}",
                    f"Text: {chunk.text}",
                ]
            )
        )

    return "\n\n".join(formatted_chunks)


def plan_queries(state: AgentState) -> AgentState:
    """Generate retrieval-friendly queries from the user question."""
    _log_node("plan_queries")
    print(f"Question: {state['question']}")
    prompt = PLANNER_PROMPT.format(question=state["question"])
    response = planner_llm.invoke(prompt)
    queries = [query.strip() for query in response.queries if query.strip()]
    updated_state = state.copy()
    updated_state["rewritten_queries"] = queries[:4] if queries else [state["question"]]
    _log_queries("Planned queries:", updated_state["rewritten_queries"])
    return updated_state


def retrieve_evidence(state: AgentState) -> AgentState:
    """Search the vector store for each planned query and accumulate unique evidence."""
    _log_node("retrieve_evidence")
    _log_queries("Queries used for retrieval:", state["rewritten_queries"])
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
    print(f"Retrieval attempts so far: {updated_state['attempts']}")
    _log_retrieved_chunks(updated_state["retrieved_chunks"])
    return updated_state


def evaluate_evidence(state: AgentState) -> AgentState:
    """Decide whether the retrieved evidence is sufficient to answer safely."""
    _log_node("evaluate_evidence")
    evidence = format_evidence(state["retrieved_chunks"])
    prompt = EVIDENCE_EVALUATOR_PROMPT.format(
        question=state["question"],
        evidence=evidence,
    )
    response = evaluator_llm.invoke(prompt)

    updated_state = state.copy()
    updated_state["evidence_sufficient"] = response.sufficient
    print(f"Evidence sufficient: {updated_state['evidence_sufficient']}")
    return updated_state


def rewrite_queries_for_retry(state: AgentState) -> AgentState:
    """Rewrite queries for a second retrieval attempt when evidence is weak."""
    _log_node("rewrite_queries_for_retry")
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
    _log_queries("Retry queries:", updated_state["rewritten_queries"])
    return updated_state


def generate_answer(state: AgentState) -> AgentState:
    """Create the final grounded answer or quiz from retrieved evidence."""
    _log_node("generate_answer")
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
    print(f"Answer generated. Length: {len(response_text)} characters")
    return updated_state


def decide_next_step(state: AgentState) -> str:
    """Choose whether to retry retrieval or finish with answer generation."""
    _log_node("decide_next_step")
    if state["evidence_sufficient"]:
        print("Decision: generate_answer (evidence is sufficient)")
        return "generate_answer"

    if state["attempts"] >= MAX_ATTEMPTS:
        print("Decision: generate_answer (max attempts reached)")
        return "generate_answer"

    print("Decision: rewrite_queries_for_retry (need another retrieval attempt)")
    return "rewrite_queries_for_retry"


def build_agent_graph():
    """Create and compile the LangGraph workflow for the RAG agent."""
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
    """Run the agent workflow for a single user question."""
    initial_state: AgentState = {
        "question": question,
        "rewritten_queries": [],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 0,
    }

    return agent_app.invoke(initial_state)
