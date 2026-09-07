import sys
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType
from loguru import logger

def create_payload_indices(client, collection):
    client.create_payload_index(collection_name=collection, field_name="arxiv_id", field_schema=PayloadSchemaType.KEYWORD)
