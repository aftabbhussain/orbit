from loguru import logger

def safe_results(hits):
    return hits if hits else []
