import sys
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from loguru import logger

def upsert_batch(client, collection, points):
    client.upsert(collection_name=collection, points=points)
