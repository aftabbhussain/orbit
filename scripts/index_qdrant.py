import sys
from pathlib import Path
from qdrant_client import QdrantClient
from loguru import logger

BATCH_SIZE = 64
