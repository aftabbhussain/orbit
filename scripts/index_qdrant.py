import sys
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from fastembed import TextEmbedding
from loguru import logger

embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
