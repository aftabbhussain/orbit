import os
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from loguru import logger

RAW_DIR = Path("data/raw")

def fetch_papers(query="cat:cs.CL", max_results=10):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Querying arXiv API for {query}")
