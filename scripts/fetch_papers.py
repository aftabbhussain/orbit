import os
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from loguru import logger

RAW_DIR = Path("data/raw")
CATEGORIES = ["cs.CL", "cs.AI", "cs.LG"]

def download_with_retry(url, target_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ResearchAssistant/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp, open(target_path, "wb") as out:
                out.write(resp.read())
            logger.info(f"Successfully downloaded {target_path.name}")
            return True
        except Exception as e:
            logger.warning(f"Download error on {url} (attempt {attempt+1}): {e}")
            time.sleep(2)
    return False
