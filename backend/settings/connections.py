from qdrant_client import QdrantClient
from elasticsearch import Elasticsearch
from loguru import logger

def check_connections():
    try:
        es = get_elasticsearch_client()
        logger.info(f"Elasticsearch ping: {es.ping()}")
    except Exception as e:
        logger.error(f"Failed to ping Elasticsearch: {e}")
