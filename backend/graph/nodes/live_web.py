from langgraph.errors import NodeInterrupt
from loguru import logger

from backend.graph.context import ConversationState
from backend.retrieval.ranker import WebSearch


def web_search_node(state: ConversationState) -> dict:
    query = state.get("query", "")
    try:
        searcher = WebSearch()
        if not searcher.is_available():
            raise NodeInterrupt("Service temporarily unavailable", id="web_search")

        results = searcher.search(query)
        doc_payloads = [
            {
                "id": doc.id,
                "content": doc.content,
                "title": doc.title,
                "score": doc.score,
                "source": doc.source,
                "metadata": doc.metadata,
            }
            for doc in results
        ]

        return {
            "document": doc_payloads,
            "reasoning_step": [f"WEB_SEARCH: Retrieved {len(doc_payloads)} result"],
        }

    except NodeInterrupt:
        raise
    except Exception as exc:
        logger.error(f"[LiveWeb] Search failed: {exc}")
        raise NodeInterrupt("Service temporarily unavailable", id="web_search")


live_web_node = web_search_node
