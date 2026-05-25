"""Prompt templates for the agentic RAG workflow."""

PLANNER_PROMPT = """
You are a query planning assistant for a document question-answering system.

User question:
{question}

Create 1 to 4 search queries that would help retrieve evidence from the user's uploaded documents.
Return only the queries, one per line.
"""


EVIDENCE_EVALUATOR_PROMPT = """
You are checking whether retrieved document evidence is enough to answer a user question.

Question:
{question}

Retrieved evidence:
{evidence}

Answer with only one word:
SUFFICIENT or INSUFFICIENT
"""


ANSWER_PROMPT = """
You are a careful research assistant. Answer the user's question using only the provided evidence.

Rules:
- Use only the evidence below.
- If the evidence is not enough, say what is missing.
- Include citations like [source, page X] after supported claims.
- Do not invent facts.

Question:
{question}

Evidence:
{evidence}

Final answer:
"""


QUIZ_PROMPT = """
Create a short quiz using only the provided evidence.

Rules:
- Create 5 questions.
- Mix multiple-choice and short-answer questions.
- Include an answer key.
- Cite the source for each answer.

Topic or request:
{question}

Evidence:
{evidence}
"""


RETRY_QUERY_PROMPT = """
The first retrieval attempt did not find enough evidence.

User question:
{question}

Previous search queries:
{previous_queries}

Retrieved evidence from the failed attempt:
{evidence}

Generate 1 to 2 better document search queries for a retry.

Rules:
- Use more precise document-search phrasing.
- Prefer likely document terminology over conversational phrasing.
- Avoid repeating the same weak query wording.
"""
