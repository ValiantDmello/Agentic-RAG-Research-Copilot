from src.agent import (
    EvidenceEvaluation,
    QueryPlan,
    RetryQueryPlan,
    build_agent_graph,
    decide_next_step,
    evaluate_evidence,
    format_evidence,
    generate_answer,
    plan_queries,
    rewrite_queries_for_retry,
    retrieve_evidence,
)
from src.schemas import RetrievedChunk


class FakePlannerLLM:
    def __init__(self, queries: list[str]) -> None:
        self.queries = queries
        self.prompts: list[str] = []

    def invoke(self, prompt: str) -> QueryPlan:
        self.prompts.append(prompt)
        return QueryPlan(queries=self.queries)


class FakeRetryPlannerLLM:
    def __init__(self, queries: list[str]) -> None:
        self.queries = queries
        self.prompts: list[str] = []

    def invoke(self, prompt: str) -> RetryQueryPlan:
        self.prompts.append(prompt)
        return RetryQueryPlan(queries=self.queries)


class FakeTextLLM:
    def __init__(self, sufficient: bool) -> None:
        self.sufficient = sufficient
        self.prompts: list[str] = []

    def invoke(self, prompt: str) -> EvidenceEvaluation:
        self.prompts.append(prompt)
        return EvidenceEvaluation(sufficient=self.sufficient)


class FakeAnswerResponse:
    def __init__(self, content: str) -> None:
        self.content = content


class FakeAnswerLLM:
    def __init__(self, content: str) -> None:
        self.content = content
        self.prompts: list[str] = []

    def invoke(self, prompt: str) -> FakeAnswerResponse:
        self.prompts.append(prompt)
        return FakeAnswerResponse(self.content)


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


def test_retrieve_evidence_preserves_prior_chunks_across_retries(monkeypatch) -> None:
    """Later retrieval attempts should keep earlier useful chunks and add only new ones."""
    prior_chunk = RetrievedChunk(
        chunk_id="doc::page-1::chunk-0",
        text="Useful evidence from the first attempt.",
        source="doc.md",
        page=1,
        score=0.92,
    )
    repeated_chunk = RetrievedChunk(
        chunk_id="doc::page-1::chunk-0",
        text="Useful evidence from the first attempt.",
        source="doc.md",
        page=1,
        score=0.92,
    )
    new_chunk = RetrievedChunk(
        chunk_id="doc::page-4::chunk-2",
        text="New evidence found during the retry attempt.",
        source="doc.md",
        page=4,
        score=0.89,
    )
    search_calls: list[tuple[str, int]] = []

    def fake_search_documents(query: str, k: int = 5) -> list[RetrievedChunk]:
        search_calls.append((query, k))
        return [repeated_chunk, new_chunk]

    monkeypatch.setattr("src.agent.search_documents", fake_search_documents)

    initial_state = {
        "question": "How was the system validated?",
        "rewritten_queries": ["validation details"],
        "retrieved_chunks": [prior_chunk],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 1,
    }

    result = retrieve_evidence(initial_state)

    assert search_calls == [("validation details", 4)]
    assert [chunk.chunk_id for chunk in result["retrieved_chunks"]] == [
        "doc::page-1::chunk-0",
        "doc::page-4::chunk-2",
    ]
    assert result["attempts"] == 2
    assert len(result["retrieved_chunks"]) == 2


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


def test_evaluate_evidence_marks_state_sufficient_when_llm_says_sufficient(
    monkeypatch,
) -> None:
    """Evaluator should set the sufficiency flag when the model approves the evidence."""
    fake_llm = FakeTextLLM(True)
    monkeypatch.setattr("src.agent.evaluator_llm", fake_llm)
    retrieved_chunk = RetrievedChunk(
        chunk_id="doc::page-4::chunk-0",
        text="A grounded supporting passage.",
        source="doc.md",
        page=4,
        score=0.93,
    )
    initial_state = {
        "question": "What is the main conclusion?",
        "rewritten_queries": ["main conclusion"],
        "retrieved_chunks": [retrieved_chunk],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 1,
    }

    result = evaluate_evidence(initial_state)

    assert result["evidence_sufficient"] is True
    assert initial_state["evidence_sufficient"] is False
    assert len(fake_llm.prompts) == 1
    assert "Question:\nWhat is the main conclusion?" in fake_llm.prompts[0]
    assert "[Evidence 1] Source: doc.md, page 4" in fake_llm.prompts[0]
    assert "Chunk ID: doc::page-4::chunk-0" in fake_llm.prompts[0]
    assert "Text: A grounded supporting passage." in fake_llm.prompts[0]


def test_evaluate_evidence_marks_state_insufficient_for_any_non_sufficient_reply(
    monkeypatch,
) -> None:
    """Evaluator should use the structured boolean decision from the model output."""
    fake_llm = FakeTextLLM(False)
    monkeypatch.setattr("src.agent.evaluator_llm", fake_llm)
    initial_state = {
        "question": "How was the method validated?",
        "rewritten_queries": ["method validation"],
        "retrieved_chunks": [],
        "evidence_sufficient": True,
        "answer": "",
        "attempts": 1,
    }

    result = evaluate_evidence(initial_state)

    assert result["evidence_sufficient"] is False


def test_rewrite_queries_for_retry_overwrites_queries_with_retry_plan(
    monkeypatch,
) -> None:
    """Retry rewriting should replace the old search plan with cleaner retry queries."""
    fake_llm = FakeRetryPlannerLLM([" narrower concept ", "author terminology"])
    monkeypatch.setattr("src.agent.retry_planner_llm", fake_llm)
    retrieved_chunk = RetrievedChunk(
        chunk_id="doc::page-2::chunk-1",
        text="A partial passage that was not enough.",
        source="doc.md",
        page=2,
        score=0.61,
    )
    initial_state = {
        "question": "How does the system validate its findings?",
        "rewritten_queries": ["validate findings", "system validation"],
        "retrieved_chunks": [retrieved_chunk],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 1,
    }

    result = rewrite_queries_for_retry(initial_state)

    assert result["rewritten_queries"] == ["narrower concept", "author terminology"]
    assert initial_state["rewritten_queries"] == ["validate findings", "system validation"]
    assert len(fake_llm.prompts) == 1
    assert "The first retrieval attempt did not find enough evidence." in fake_llm.prompts[0]
    assert "User question:\nHow does the system validate its findings?" in fake_llm.prompts[0]
    assert "Previous search queries:\n- validate findings\n- system validation" in fake_llm.prompts[0]
    assert "[Evidence 1] Source: doc.md, page 2" in fake_llm.prompts[0]


def test_rewrite_queries_for_retry_falls_back_to_original_question_when_empty(
    monkeypatch,
) -> None:
    """If the retry planner returns only blanks, keep the original question as the query."""
    fake_llm = FakeRetryPlannerLLM([" ", ""])
    monkeypatch.setattr("src.agent.retry_planner_llm", fake_llm)
    initial_state = {
        "question": "What changed in the revised architecture?",
        "rewritten_queries": ["revised architecture"],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 1,
    }

    result = rewrite_queries_for_retry(initial_state)

    assert result["rewritten_queries"] == ["What changed in the revised architecture?"]


def test_generate_answer_uses_answer_prompt_and_stores_response(monkeypatch) -> None:
    """Standard questions should use the answer prompt and save the model's reply."""
    fake_llm = FakeAnswerLLM("The main conclusion is supported by the document. [doc.md, page 3]")
    monkeypatch.setattr("src.agent.llm", fake_llm)
    retrieved_chunk = RetrievedChunk(
        chunk_id="doc::page-3::chunk-0",
        text="The report concludes that retrieval quality dominates answer quality.",
        source="doc.md",
        page=3,
        score=0.95,
    )
    initial_state = {
        "question": "What is the main conclusion?",
        "rewritten_queries": ["main conclusion"],
        "retrieved_chunks": [retrieved_chunk],
        "evidence_sufficient": True,
        "answer": "",
        "attempts": 1,
    }

    result = generate_answer(initial_state)

    assert result["answer"] == "The main conclusion is supported by the document. [doc.md, page 3]"
    assert initial_state["answer"] == ""
    assert len(fake_llm.prompts) == 1
    assert "Final answer:" in fake_llm.prompts[0]
    assert "Question:\nWhat is the main conclusion?" in fake_llm.prompts[0]
    assert "[Evidence 1] Source: doc.md, page 3" in fake_llm.prompts[0]


def test_generate_answer_uses_quiz_prompt_when_question_requests_quiz(
    monkeypatch,
) -> None:
    """Quiz requests should route to the quiz prompt instead of the normal answer prompt."""
    fake_llm = FakeAnswerLLM("1. Question...\nAnswer key: ...")
    monkeypatch.setattr("src.agent.llm", fake_llm)
    initial_state = {
        "question": "Create a quiz about this document.",
        "rewritten_queries": ["document quiz"],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 2,
    }

    result = generate_answer(initial_state)

    assert result["answer"] == "1. Question...\nAnswer key: ..."
    assert len(fake_llm.prompts) == 1
    assert "Create a short quiz using only the provided evidence." in fake_llm.prompts[0]
    assert "Topic or request:\nCreate a quiz about this document." in fake_llm.prompts[0]


def test_decide_next_step_returns_generate_answer_when_evidence_is_sufficient() -> None:
    """Sufficient evidence should skip retries and move straight to answer generation."""
    state = {
        "question": "What is the conclusion?",
        "rewritten_queries": [],
        "retrieved_chunks": [],
        "evidence_sufficient": True,
        "answer": "",
        "attempts": 1,
    }

    assert decide_next_step(state) == "generate_answer"


def test_decide_next_step_returns_retry_when_evidence_is_weak_and_attempts_remain() -> None:
    """Weak evidence should trigger a retry while the workflow is still under the limit."""
    state = {
        "question": "What is the conclusion?",
        "rewritten_queries": [],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 1,
    }

    assert decide_next_step(state) == "rewrite_queries_for_retry"


def test_decide_next_step_returns_generate_answer_at_max_attempts() -> None:
    """Once the retry limit is reached, the workflow should stop retrying."""
    state = {
        "question": "What is the conclusion?",
        "rewritten_queries": [],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 2,
    }

    assert decide_next_step(state) == "generate_answer"


def test_build_agent_graph_returns_compiled_graph() -> None:
    """Graph construction should compile into an invokable LangGraph app."""
    graph = build_agent_graph()

    assert hasattr(graph, "invoke")


def test_build_agent_graph_executes_happy_path_with_mocked_nodes(monkeypatch) -> None:
    """The compiled graph should move from planning to answer generation on sufficient evidence."""
    call_order: list[str] = []

    def fake_plan_queries(state):
        call_order.append("plan_queries")
        updated = state.copy()
        updated["rewritten_queries"] = ["planned query"]
        return updated

    def fake_retrieve_evidence(state):
        call_order.append("retrieve_evidence")
        updated = state.copy()
        updated["retrieved_chunks"] = []
        updated["attempts"] = state["attempts"] + 1
        return updated

    def fake_evaluate_evidence(state):
        call_order.append("evaluate_evidence")
        updated = state.copy()
        updated["evidence_sufficient"] = True
        return updated

    def fake_generate_answer(state):
        call_order.append("generate_answer")
        updated = state.copy()
        updated["answer"] = "Grounded answer"
        return updated

    monkeypatch.setattr("src.agent.plan_queries", fake_plan_queries)
    monkeypatch.setattr("src.agent.retrieve_evidence", fake_retrieve_evidence)
    monkeypatch.setattr("src.agent.evaluate_evidence", fake_evaluate_evidence)
    monkeypatch.setattr("src.agent.generate_answer", fake_generate_answer)

    graph = build_agent_graph()
    initial_state = {
        "question": "What is the conclusion?",
        "rewritten_queries": [],
        "retrieved_chunks": [],
        "evidence_sufficient": False,
        "answer": "",
        "attempts": 0,
    }

    result = graph.invoke(initial_state)

    assert call_order == [
        "plan_queries",
        "retrieve_evidence",
        "evaluate_evidence",
        "generate_answer",
    ]
    assert result["answer"] == "Grounded answer"
    assert result["evidence_sufficient"] is True
