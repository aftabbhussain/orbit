from loguru import logger

def handle_empty_retrieval():
    logger.warning("No academic literature found for query, flagging fallback")
