from langgraph.errors import GraphRecursionError
from loguru import logger

def safe_run():
    logger.info("Executing safe graph execution with recursion guard")
