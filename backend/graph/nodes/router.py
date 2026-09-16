from loguru import logger
from backend.graph.context import ConversationState

def router_node(state: ConversationState) -> dict:
    logger.info("Routing query")
    return {"next_step": "knowledge_lookup"}
