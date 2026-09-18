from loguru import logger
from backend.graph.context import ConversationState

def live_web_node(state: ConversationState) -> dict:
    logger.info("Executing live web search fallback")
    return {}
