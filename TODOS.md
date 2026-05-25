# Step 12 TODOs: Build the Agentic Workflow with LangGraph

This file is a teaching-first roadmap for implementing **Step 12 — Build the Agentic Workflow with LangGraph** from [agentic_rag_implementation_guide.md](/c:/Users/vvd09/OneDrive/Desktop/Vali/Projects/rag-project/agentic_rag_implementation_guide.md).

The goal is not just to "make it work". The goal is to understand:

- what problem LangGraph solves in a RAG app
- why this workflow should be stateful
- how each node contributes to reliability
- how retrieval, evaluation, retries, and answer generation fit together

---

## 1. First understand the purpose of Step 12

Before this step, your app can retrieve chunks for a query.

That is useful, but it is still a **single-shot RAG pipeline**:

1. user asks one question
2. system searches once
3. system answers once

Step 12 turns that into an **agentic workflow**.

What we are trying to achieve:

- Let the system think in stages instead of one big prompt.
- Let it plan better search queries before retrieval.
- Let it judge whether the retrieved evidence is good enough.
- Let it retry retrieval if the first search was weak.
- Let it produce a safer final answer when evidence is incomplete.

Why this matters:

- real user questions are often vague or broad
- the first query is often not the best retrieval query
- retrieval quality is one of the biggest factors in RAG quality
- a reliable assistant should know when it does not know enough

What LangGraph adds:

- a clean way to model the workflow as nodes and transitions
- explicit state passed between steps
- conditional branching such as "retry" vs "answer now"
- a structure that is easier to debug, test, and extend

The core mindset:

- **Do not think of this as "calling the LLM a few times".**
- Think of it as **building a small state machine for grounded reasoning**.

---

## 2. Mental model of the workflow

The first version of the graph should look like this:

1. `plan_queries`
2. `retrieve_evidence`
3. `evaluate_evidence`
4. if evidence is enough -> `generate_answer`
5. if evidence is not enough and retries remain -> `rewrite_queries_for_retry`
6. then go back to `retrieve_evidence`

That means your system is doing:

- planning
- acting
- checking
- retrying
- answering

This is the heart of agentic RAG.

---

## 3. Implementation strategy

We should implement this in small, testable pieces instead of writing the whole graph at once.

Recommended order:

1. define workflow state
2. create the LLM entry point
3. build evidence formatting
4. implement each node one by one
5. implement the decision function
6. wire the LangGraph graph
7. add a public `answer_question()` function
8. add focused tests for node behavior and graph flow

---

## 4. TODOs

## TODO 1: Add an `AgentState` schema in `src/schemas.py`

What we are trying to achieve:

- define the shared state that every LangGraph node reads from and writes to

Why:

- LangGraph works best when the workflow state is explicit
- this makes the graph understandable and predictable
- without a clear state object, node logic becomes messy fast

What to add:

- a typed structure for:
  - `question`
  - `rewritten_queries`
  - `retrieved_chunks`
  - `evidence_sufficient`
  - `answer`
  - `attempts`

Recommended design choice:

- keep using strong typing
- since the project already uses Pydantic models for chunks, make `retrieved_chunks` a list of `RetrievedChunk`
- define `AgentState` with `TypedDict`

Suggested shape:

```python
class AgentState(TypedDict):
    question: str
    rewritten_queries: list[str]
    retrieved_chunks: list[RetrievedChunk]
    evidence_sufficient: bool
    answer: str
    attempts: int
```

What to learn here:

- the graph state is the memory of the workflow
- every node should only update the parts of state it is responsible for

Done when:

- `src/schemas.py` includes `AgentState`
- type hints across the upcoming agent code feel natural instead of forced

---

## TODO 2: Create `src/agent.py`

What we are trying to achieve:

- create one home for the LangGraph workflow

Why:

- Step 12 is the orchestration layer of the app
- keeping workflow code in one file makes it much easier to read and debug

What to include initially:

- imports
- `llm = ChatOpenAI(...)`
- `MAX_ATTEMPTS`
- helper functions
- node functions
- graph builder
- public entry point function

Important design principle:

- keep node functions small and single-purpose
- each node should answer one question:
  - planning node: "what should we search?"
  - retrieval node: "what evidence did we find?"
  - evaluator node: "is this enough?"
  - retry node: "how should we search differently?"
  - answer node: "what should we say?"

Done when:

- `src/agent.py` exists with placeholders or skeletons for all graph parts

---

## TODO 3: Initialize the LLM in `src/agent.py`

What we are trying to achieve:

- create the model object used by planning, evaluation, retry rewriting, and answer generation

Why:

- this keeps model configuration centralized
- temperature `0` is important here because reliability matters more than creativity

Implementation notes:

- import `ChatOpenAI`
- import `OPENAI_MODEL` from `src.config`
- create:

```python
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
```

What to learn here:

- in agentic RAG, different nodes may use the same model but for different jobs
- the model is not just "the answer generator"; it also acts as planner and evaluator

Stretch idea for later:

- separate answer model and planner/evaluator model if you want different cost/performance tradeoffs

Done when:

- your agent module has a reusable LLM instance

---

## TODO 4: Implement `format_evidence()`

What we are trying to achieve:

- turn retrieved chunks into a prompt-friendly evidence block

Why:

- raw Python objects are not useful to the LLM
- the evaluator and answer generator both need the evidence in a clear, structured format

What this function should do:

- accept `list[RetrievedChunk]`
- include:
  - source
  - optional page
  - chunk id
  - text
- return one combined string

Why chunk IDs matter:

- they help trace what the model saw
- they make debugging retrieval much easier

What to learn here:

- prompt formatting is part of system design, not just presentation
- clearer evidence formatting usually improves grounded responses

Done when:

- you can pass retrieved chunks into prompts consistently

---

## TODO 5: Implement `plan_queries(state)`

What we are trying to achieve:

- convert the user question into better search queries

Why:

- user questions are often phrased for conversation, not retrieval
- retrieval often works better with focused, concrete search queries
- one broad question can be split into several narrower retrieval attempts

What this node should do:

1. read `state["question"]`
2. format `PLANNER_PROMPT`
3. call the LLM
4. parse one-query-per-line output
5. store up to 4 queries in `state["rewritten_queries"]`
6. fall back to the original question if parsing fails

What to pay attention to:

- robust parsing matters
- strip bullets and blank lines
- do not assume the model will follow instructions perfectly

What to learn here:

- planning is not magic; it is just transforming a user request into retrieval-friendly subqueries
- a lot of "agent intelligence" is really careful decomposition

Good manual test questions:

- "Compare innate and adaptive immunity."
- "Summarize the document and explain the author’s main argument."
- "Create a quiz about the retrieval architecture in this paper."

Done when:

- the node produces a short list of clean search queries

---

## TODO 6: Implement `retrieve_evidence(state)`

What we are trying to achieve:

- run retrieval for each planned query and merge the results

Why:

- one search query may miss useful chunks
- multi-query retrieval gives broader coverage
- the graph needs a single place where retrieval happens

What this node should do:

1. loop through `state["rewritten_queries"]`
2. call `search_documents(query, k=4)` or similar
3. collect all `RetrievedChunk` results
4. deduplicate by `chunk_id`
5. save them to `state["retrieved_chunks"]`
6. increment `state["attempts"]`

Important design decision:

- deduplication is essential
- if two queries retrieve the same chunk, we want it once in the evidence list

Subtle thing to think about:

- should a retry replace old chunks or add to them?
- for the first implementation, replacing the evidence list is simpler and easier to reason about

What to learn here:

- agentic retrieval is often just repeated retrieval with better queries and deduplication

Done when:

- the node reliably gathers a clean evidence set from multiple searches

---

## TODO 7: Implement `evaluate_evidence(state)`

What we are trying to achieve:

- let the system decide if the current evidence is enough to answer safely

Why:

- retrieval alone does not guarantee answerability
- the assistant should not answer confidently when the evidence is thin or irrelevant

What this node should do:

1. format evidence with `format_evidence()`
2. format `EVIDENCE_EVALUATOR_PROMPT`
3. call the LLM
4. parse the result
5. set `state["evidence_sufficient"]`

For the first implementation:

- keep the prompt simple
- treat responses starting with `SUFFICIENT` as true
- everything else becomes false

What to learn here:

- this node is the safety gate of the workflow
- the value of agentic RAG is not only better retrieval, but also better refusal behavior

Caution:

- this evaluator is still heuristic because it is LLM-based
- later you can improve it by returning structured JSON with missing-information details

Done when:

- the graph can branch based on evidence quality instead of always answering

---

## TODO 8: Implement `rewrite_queries_for_retry(state)`

What we are trying to achieve:

- generate a second, hopefully better search strategy when the first retrieval attempt failed

Why:

- many failures happen because the initial queries were too broad, too literal, or missing key terms
- a retry step gives the system one more chance before answering cautiously

What this node should do:

1. explain to the model that the first search was insufficient
2. ask for 2 better search queries
3. parse the response
4. overwrite `state["rewritten_queries"]`
5. fall back to the original question if needed

Why overwrite instead of append:

- simpler graph behavior
- easier debugging
- makes the second attempt clearly different from the first

What to learn here:

- retries should be intentional, not random repetition
- the point is to change the search space

Done when:

- the second retrieval attempt is meaningfully different from the first one

---

## TODO 9: Implement `generate_answer(state)`

What we are trying to achieve:

- produce the final user-facing output using only the retrieved evidence

Why:

- this is where the workflow becomes useful to the user
- all earlier nodes exist to make this answer more grounded and reliable

What this node should do:

1. format evidence
2. choose prompt:
  - `QUIZ_PROMPT` if the question asks for a quiz
  - otherwise `ANSWER_PROMPT`
3. call the LLM
4. store the text in `state["answer"]`

What to learn here:

- answer generation should be the last step, not the first
- in a reliable RAG pipeline, answering is downstream from retrieval and evidence checks

Future improvement:

- later you can decide answer mode more explicitly instead of only checking for the word `"quiz"`

Done when:

- the graph returns a grounded answer even when evidence is incomplete

---

## TODO 10: Implement `decide_next_step(state)`

What we are trying to achieve:

- define the branching logic after evidence evaluation

Why:

- LangGraph needs a decision function to know which node to run next
- this is where you encode retry policy

Logic for the MVP:

1. if evidence is sufficient -> go to `generate_answer`
2. if attempts reached `MAX_ATTEMPTS` -> go to `generate_answer`
3. otherwise -> go to `rewrite_queries_for_retry`

Why answer even when evidence is insufficient after max retries:

- because the system should still respond
- but it should respond cautiously and explain what is missing
- your answer prompt already asks for that behavior

What to learn here:

- agentic systems need explicit stopping conditions
- retries without limits create loops and unpredictable cost

Done when:

- the graph has a bounded, understandable retry policy

---

## TODO 11: Build the LangGraph in `build_agent_graph()`

What we are trying to achieve:

- connect all nodes into one executable workflow

Why:

- the nodes only become a real agent when transitions are wired together

What to implement:

- create `StateGraph(AgentState)`
- register nodes:
  - `plan_queries`
  - `retrieve_evidence`
  - `evaluate_evidence`
  - `rewrite_queries_for_retry`
  - `generate_answer`
- set entry point to `plan_queries`
- add normal edges:
  - `plan_queries -> retrieve_evidence`
  - `retrieve_evidence -> evaluate_evidence`
  - `rewrite_queries_for_retry -> retrieve_evidence`
  - `generate_answer -> END`
- add conditional edges from `evaluate_evidence`

What to learn here:

- LangGraph is basically a typed workflow engine for LLM applications
- the graph makes your orchestration visible instead of burying it in one function

Done when:

- the graph compiles successfully

---

## TODO 12: Create `agent_app = build_agent_graph()`

What we are trying to achieve:

- compile the graph once and reuse it

Why:

- avoids rebuilding the graph for every question
- keeps the public API simple

Done when:

- the compiled graph is stored at module level

---

## TODO 13: Add `answer_question(question: str) -> dict`

What we are trying to achieve:

- provide a simple function that the rest of the app can call

Why:

- Streamlit or FastAPI should not need to know graph internals
- this creates a clean boundary between the UI and orchestration layer

What this function should do:

1. create the initial `AgentState`
2. invoke the compiled graph
3. return the final state

Initial state should include:

- original question
- empty query list
- empty retrieved chunk list
- `False` for evidence sufficiency
- empty answer
- `0` attempts

What to learn here:

- good architecture hides workflow complexity behind a simple interface

Done when:

- the future UI can call one function and get the full workflow result

---

## TODO 14: Add focused tests for the agent workflow

What we are trying to achieve:

- test orchestration behavior without relying on live API calls

Why:

- this is the most important logic in the project
- if this breaks, your app may hallucinate, loop incorrectly, or skip retries
- tests here protect the reliability promise of the project

What to test first:

- `format_evidence()` formats source, page, chunk id, and text
- `plan_queries()` falls back to the original question if parsing produces nothing
- `retrieve_evidence()` deduplicates chunks by `chunk_id`
- `decide_next_step()` returns the correct branch in all three cases:
  - sufficient evidence
  - insufficient evidence but retries remain
  - insufficient evidence and max attempts reached
- `answer_question()` or the graph flow reaches answer generation

How to test safely:

- monkeypatch the LLM calls
- monkeypatch `search_documents`
- avoid real OpenAI requests in tests

Suggested test file:

- `tests/test_agent.py`

Important note:

- your project instructions say not to run the whole test suite unless you wrote new tests
- once this file exists, it is okay to run only that specific test file

Done when:

- the core graph behavior is covered by deterministic unit tests

---

## TODO 15: Add logging or inspectable outputs for learning

What we are trying to achieve:

- make the workflow easy to inspect while you learn

Why:

- agentic systems are much easier to understand when you can see intermediate state
- this directly matches the project rule to log planned sub-questions, retrieved chunks, and grounding-style checks

Simple first version:

- return the final state exactly as the graph produces it
- inspect:
  - `rewritten_queries`
  - `retrieved_chunks`
  - `attempts`
  - `evidence_sufficient`

What to learn here:

- observability is part of good agent design
- if you cannot inspect the workflow, debugging RAG quality becomes guesswork

Done when:

- you can explain why the agent answered the way it did

---

## 5. Recommended implementation order for you

If you want to learn this hands-on without getting overwhelmed, use this exact order:

1. add `AgentState` to `src/schemas.py`
2. create `src/agent.py` with imports, `llm`, and `MAX_ATTEMPTS`
3. implement `format_evidence()`
4. implement `plan_queries()`
5. implement `retrieve_evidence()`
6. implement `evaluate_evidence()`
7. implement `rewrite_queries_for_retry()`
8. implement `generate_answer()`
9. implement `decide_next_step()`
10. build and compile the graph
11. add `answer_question()`
12. add `tests/test_agent.py`

Reason for this order:

- it moves from data definition -> helpers -> nodes -> branching -> full graph -> tests
- that keeps complexity low at each step

---

## 6. Questions you should be able to answer after Step 12

If you can answer these, you truly understand the step:

1. Why is a graph better here than one large prompt?
2. Why do we separate planning, retrieval, evaluation, and answer generation?
3. What does the workflow state represent?
4. Why do we need a retry limit?
5. Why is evidence evaluation important for RAG safety?
6. Why should answer generation happen after evidence sufficiency checking?
7. Why is deduplication useful in multi-query retrieval?

---

## 7. Practical warnings while implementing

- Do not let node functions silently depend on hidden global state other than the shared LLM and configuration.
- Do not skip fallback behavior when parsing LLM outputs.
- Do not make retries unbounded.
- Do not answer from the model without passing retrieved evidence into the prompt.
- Do not throw away chunk metadata like source and page; that metadata is how citations happen.

---

## 8. Nice improvements after the MVP graph works

These are not required for the first pass, but they are excellent follow-up learning tasks:

- return structured JSON from the evaluator instead of plain text
- add a question classifier node before planning
- separate quiz generation into its own route or node
- track retrieval scores and optionally filter low-confidence chunks
- add grounding checks after answer generation
- preserve retrieval history across attempts for better debugging

---

## 9. Definition of done for Step 12

You can consider Step 12 complete when all of these are true:

- `src/agent.py` exists and compiles
- `AgentState` is defined in `src/schemas.py`
- the graph plans queries before retrieving
- retrieval can happen more than once
- evidence sufficiency controls branching
- retries stop at a fixed limit
- the final answer is generated from retrieved evidence
- the final returned result includes enough intermediate state to inspect what happened
- focused tests exist for the workflow logic

---

## 10. Best way to learn this from here

The best next move is:

1. implement only `AgentState` and the `src/agent.py` skeleton first
2. then implement one node at a time
3. after each node, read the code and explain out loud:
   "What state does this node read, what state does it write, and why?"

That habit will teach you LangGraph much faster than copying the full example at once.
