import time
from langgraph.errors import NodeInterrupt
from loguru import logger

from backend.graph.context import ConversationState
from backend.retrieval.ranker import HybridIndex


def vector_search_node(state: ConversationState) -> dict:
    query = state.get("query", "")
    existing_timings = state.get("node_timings", {})

    t0 = time.time()
    try:
        searcher = HybridIndex()
        matches = searcher.search(query, top_k=5)
        duration = (time.time() - t0) * 1000
        updated_timings = {**existing_timings, "vector_search": duration}

        serializable_docs = [
            {
                "id": doc.id,
                "content": doc.content,
                "title": doc.title,
                "score": doc.score,
                "source": doc.source,
                "metadata": doc.metadata,
            }
            for doc in matches
        ]

        summary_note = (
            f"VECTOR_SEARCH: Retrieved {len(serializable_docs)} document for: "
            f"{query[:50]}..."
        )

        return {
            "document": serializable_docs,
            "reasoning_step": state.get("reasoning_step", []) + [summary_note],
            "node_timings": updated_timings,
        }
    except Exception as err:
        logger.error(f"[KnowledgeLookup] Search failed: {err}")
        raise NodeInterrupt("Service temporarily unavailable", id="vector_search")


lookup_knowledge_node = vector_search_node
