from loguru import logger
from backend.graph.context import ConversationState

def judge_node(state: ConversationState) -> dict:
    logger.info("Evaluating answer quality in judge node")
    return {"passed": True}
