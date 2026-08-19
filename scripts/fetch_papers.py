import os
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from loguru import logger

RAW_DIR = Path("data/raw")
CATEGORIES = ["cs.CL", "cs.AI", "cs.LG"]

def is_already_downloaded(arxiv_id):
    clean_id = arxiv_id.split("/")[-1].replace("v1", "").replace("v2", "")
    target = RAW_DIR / f"{clean_id}.pdf"
    return target.exists() and target.stat().st_size > 1024
