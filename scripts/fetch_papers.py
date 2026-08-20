"""
Paper Fetcher Utility with Rate-Limiting Protection
"""
import os
import time
import urllib.request
from pathlib import Path
from loguru import logger

RAW_DIR = Path("data/raw")
API_DELAY_SECONDS = 3.0
