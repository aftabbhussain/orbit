import time
from datetime import datetime

from langgraph.errors import NodeInterrupt

from backend.graph.context import ConversationState
from backend.settings.connections import get_llm_client
from backend.settings.prompts import (
    DIRECT_ANSWER_SYSTEM_PROMPT,
    GENERATE_SYSTEM_PROMPT,
    RAG_USER_TEMPLATE,
)


def format_documents(document: list[dict]) -> str:
    sections = []
    for idx, doc in enumerate(document, 1):
        title = doc.get("title", "Unknown")
        text = doc.get("content", "")
        metadata = doc.get("metadata", {}) or {}

        block = f"[{idx}] {title}\n{text}"
        if paper_id := metadata.get("paper_id"):
            block += f"\n[paper_id: {paper_id}]"
        elif arxiv_id := metadata.get("arxiv_id"):
            block += f"\n[arxiv_id: {arxiv_id}]"
        elif url := metadata.get("url"):
            block += f"\n[url: {url}]"

        sections.append(block)
    return "\n\n".join(sections)


def gen_node(state: ConversationState) -> dict:
    query = state.get("query", "")
    decision = state.get("decision", "process")
    docs = state.get("document", [])
    prior_timings = state.get("node_timings", {})

    llm = get_llm_client()
    if not llm:
        raise NodeInterrupt("Service temporarily unavailable", id="gen")

    if decision == "direct_answer":
        return _answer_direct(llm, query, prior_timings)

    if decision == "reject":
        reply = "I cannot help with this request."
        return {
            "answer": reply,
            "source": [],
            "reasoning_step": ["GEN: Rejected"],
            "chat_history": [
                {
                    "role": "assistant",
                    "content": reply,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
            "node_timings": prior_timings,
        }

    if decision == "clarify":
        return {
            "answer": "Could you please provide more details about what you're looking for?",
            "source": [],
            "reasoning_step": ["GEN: Clarify requested"],
            "chat_history": [],
            "node_timings": prior_timings,
        }

    return _answer_rag_context(llm, query, docs, prior_timings)


def _answer_direct(llm, query: str, timings: dict) -> dict:
    conversation = [
        {"role": "system", "content": DIRECT_ANSWER_SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    t0 = time.time()
    response = llm.invoke(conversation)
    elapsed = (time.time() - t0) * 1000
    updated_timings = {**timings, "generate": elapsed}

    return {
        "answer": response.content,
        "source": [],
        "reasoning_step": ["GEN: Direct answer"],
        "chat_history": [
            {
                "role": "assistant",
                "content": response.content,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ],
        "node_timings": updated_timings,
    }


def _answer_rag_context(
    llm, query: str, documents: list[dict], timings: dict
) -> dict:
    if not documents:
        raise NodeInterrupt("Service temporarily unavailable", id="gen")

    assembled_context = format_documents(documents)
    conversation = [
        {"role": "system", "content": GENERATE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": RAG_USER_TEMPLATE.format(
                context=assembled_context, query=query
            ),
        },
    ]

    t0 = time.time()
    response = llm.invoke(conversation)
    elapsed = (time.time() - t0) * 1000
    updated_timings = {**timings, "generate": elapsed}

    return {
        "answer": response.content,
        "source": documents,
        "reasoning_step": [f"GEN: RAG answer ({len(documents)} source)"],
        "chat_history": [
            {
                "role": "assistant",
                "content": response.content,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ],
        "node_timings": updated_timings,
    }


synthesize_answer_node = gen_node
