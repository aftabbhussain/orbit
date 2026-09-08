from qdrant_client import QdrantClient
from loguru import logger

class HybridRanker:
    def search_dense(self, query: str, top_k: int = 10):
        logger.debug(f"Executing dense vector search: {query}")
        return []
