from elasticsearch import Elasticsearch
from loguru import logger

class HybridRanker:
    def search_bm25(self, query: str, top_k: int = 10):
        logger.debug(f"Executing BM25 lexical search: {query}")
        return []
