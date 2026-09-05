from qdrant_client import QdrantClient
from elasticsearch import Elasticsearch
from loguru import logger

_qdrant_client = None
_es_client = None

def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient("http://localhost:6333")
    return _qdrant_client

def get_elasticsearch_client() -> Elasticsearch:
    global _es_client
    if _es_client is None:
        _es_client = Elasticsearch("http://localhost:9200")
    return _es_client
