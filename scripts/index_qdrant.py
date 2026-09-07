import sys
from pathlib import Path
root_path = Path(__file__).parent.parent.resolve()
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from loguru import logger

COLLECTION_NAME = "arxiv_papers"
