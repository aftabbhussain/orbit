from loguru import logger

def score_pairs(query, documents):
    pairs = [(query, d.get("content", "")) for d in documents]
    return pairs
