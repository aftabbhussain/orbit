import sys
import json
from pathlib import Path
from elasticsearch.helpers import bulk
from loguru import logger

def index_corpus():
    logger.info("Starting resilient Elasticsearch indexing")
