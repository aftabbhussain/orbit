from loguru import logger
from backend.graph.context import ConversationState

def knowledge_lookup_node(state: ConversationState) -> dict:
    logger.info("Executing knowledge lookup")
    return {}
