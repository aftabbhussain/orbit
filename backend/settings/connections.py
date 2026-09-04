from qdrant_client import QdrantClient
from loguru import logger

_qdrant_client = None

def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient("http://localhost:6333")
    return _qdrant_client
