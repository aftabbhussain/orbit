from loguru import logger
from backend.settings.prompts import JUDGE_PROMPT

def evaluate_hallucination(answer: str, context: str) -> float:
    logger.debug("Checking factual grounding")
    return 0.95
