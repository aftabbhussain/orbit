from loguru import logger
from backend.graph.context import ConversationState

def writer_node(state: ConversationState) -> dict:
    logger.info("Synthesizing answer in writer node")
    return {"answer": "Draft answer"}
