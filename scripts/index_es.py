import sys
import json
from pathlib import Path
from elasticsearch.helpers import bulk
from loguru import logger

def generate_actions(corpus_path, index_name):
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            yield {
                "_index": index_name,
                "_id": doc.get("chunk_id", doc.get("arxiv_id")),
                "_source": doc
            }
