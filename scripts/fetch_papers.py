import os
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from loguru import logger

RAW_DIR = Path("data/raw")

CATEGORIES = ["cs.CL", "cs.AI", "cs.LG"]

def build_query(categories=CATEGORIES, max_results=20):
    cat_query = "+OR+".join([f"cat:{c}" for c in categories])
    return f"http://export.arxiv.org/api/query?search_query={cat_query}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

def fetch_papers():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    url = build_query()
    logger.info(f"Fetching from URL: {url}")
