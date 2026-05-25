from src.agent import QueryPlan, format_evidence, plan_queries, retrieve_evidence
from src.schemas import RetrievedChunk


class FakePlannerLLM:
    def __init__(self, queries: list[str]) -> None:
        self.queries = queries
        self.prompts: list[str] = []

    def invoke(self, prompt: str) -> QueryPlan:
        self.prompts.append(prompt)
        return QueryPlan(queries=self.queries)


def test_format_evidence_includes_source_page_chunk_id_and_text() -> None:
    """Evidence formatting should preserve the metadata the prompts rely on."""
    chunks = [
        RetrievedChunk(
            chunk_id="sample.txt::page-2::chunk-0",
            text="Important supporting passage.",
            source="sample.txt",
            page=2,
            score=0.91,
        )
    ]

    formatted = format_evidence(chunks)

    assert "[Evidence 1] Source: sample.txt, page 2" in formatted
    assert "Chunk ID: sample.txt::page-2::chunk-0" in formatted
    assert "Text: Important supporting passage." in formatted


def test_format_evidence_omits_page_label_when_page_is_missing() -> None:
    """Chunks without page metadata should not render a fake page value."""
    chunks = [
        RetrievedChunk(
            chunk_id="notes.md::page-none::chunk-1",
            text="Ungrouped note text.",
            source="notes.md",
            page=None,
            score=0.76,
        )
    ]

    formatted = format_evidence(chunks)

    assert "[Evidence 1] Source: notes.md" in formatted
    assert ", page" not in formatted


def test_format_evidence_returns_empty_string_for_no_chunks() -> None:
    """No evidence should format to an empty prompt block."""
    assert format_evidence([]) == ""


def test_plan_queries_uses_structured_output_and_trims_queries(monkeypatch) -> None:
    """Planner output should come from the typed schema and strip extra whitespace."""
    fake_llm = FakePlannerLLM(
        [
            " innate immunity ",
            "adaptive immunity",
            "compare immune response speed",
            "first line of defense",
        ]
    )
    monkeypatch.setattr("src.agent.planner_llm", fake_llm)

    initial_state = {
        "question": "Compare innate and adaptive immunity.",
        "rewritten_queries": [],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 0,
    }

    result = plan_queries(initial_state)

    assert fake_llm.prompts == [
        (
            "\nYou are a query planning assistant for a document question-answering "
            "system.\n\nUser question:\nCompare innate and adaptive immunity.\n\n"
            "Create 1 to 4 search queries that would help retrieve evidence from "
            "the user's uploaded documents.\nReturn only the queries, one per line.\n"
        )
    ]
    assert result["rewritten_queries"] == [
        "innate immunity",
        "adaptive immunity",
        "compare immune response speed",
        "first line of defense",
    ]
    assert initial_state["rewritten_queries"] == []


def test_plan_queries_falls_back_to_original_question_when_output_is_empty(
    monkeypatch,
) -> None:
    """Empty structured planner output should fall back to the user question."""
    fake_llm = FakePlannerLLM([" ", ""])
    monkeypatch.setattr("src.agent.planner_llm", fake_llm)

    initial_state = {
        "question": "What is the main argument?",
        "rewritten_queries": [],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 0,
    }

    result = plan_queries(initial_state)

    assert result["rewritten_queries"] == ["What is the main argument?"]


def test_retrieve_evidence_merges_unique_results_from_all_queries(monkeypatch) -> None:
    """Retrieval should search each query and deduplicate repeated chunks by chunk_id."""
    chunk_a = RetrievedChunk(
        chunk_id="doc::page-1::chunk-0",
        text="First matching passage.",
        source="doc.md",
        page=1,
        score=0.91,
    )
    chunk_b = RetrievedChunk(
        chunk_id="doc::page-2::chunk-0",
        text="Second matching passage.",
        source="doc.md",
        page=2,
        score=0.88,
    )
    chunk_c = RetrievedChunk(
        chunk_id="doc::page-3::chunk-1",
        text="Third matching passage.",
        source="doc.md",
        page=3,
        score=0.84,
    )
    search_calls: list[tuple[str, int]] = []

    def fake_search_documents(query: str, k: int = 5) -> list[RetrievedChunk]:
        search_calls.append((query, k))
        if query == "innate immunity":
            return [chunk_a, chunk_b]
        if query == "adaptive immunity":
            return [chunk_b, chunk_c]
        return []

    monkeypatch.setattr("src.agent.search_documents", fake_search_documents)

    initial_state = {
        "question": "Compare innate and adaptive immunity.",
        "rewritten_queries": ["innate immunity", "adaptive immunity"],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 0,
    }

    result = retrieve_evidence(initial_state)

    assert search_calls == [("innate immunity", 4), ("adaptive immunity", 4)]
    assert [chunk.chunk_id for chunk in result["retrieved_chunks"]] == [
        "doc::page-1::chunk-0",
        "doc::page-2::chunk-0",
        "doc::page-3::chunk-1",
    ]
    assert result["attempts"] == 1
    assert initial_state["retrieved_chunks"] == []
    assert initial_state["attempts"] == 0


def test_retrieve_evidence_still_increments_attempts_when_no_matches(monkeypatch) -> None:
    """A retrieval pass counts as an attempt even if every query returns no chunks."""
    search_calls: list[tuple[str, int]] = []

    def fake_search_documents(query: str, k: int = 5) -> list[RetrievedChunk]:
        search_calls.append((query, k))
        return []

    monkeypatch.setattr("src.agent.search_documents", fake_search_documents)

    initial_state = {
        "question": "Unanswered topic",
        "rewritten_queries": ["missing concept"],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 1,
    }

    result = retrieve_evidence(initial_state)

    assert search_calls == [("missing concept", 4)]
    assert result["retrieved_chunks"] == []
    assert result["attempts"] == 2
