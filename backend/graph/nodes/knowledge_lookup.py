from loguru import logger
from backend.retrieval.ranker import HybridRanker
from backend.graph.context import ConversationState

def retrieve_context(query: str):
    logger.debug(f"Retrieving context for query: {query}")
    return []
