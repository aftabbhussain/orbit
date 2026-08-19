"""
Paper Fetcher Utility
Fetches recent and foundational academic machine learning research papers from arXiv.
Supports batch downloading, XML feed parsing, and automatic deduplication.
"""
import os
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from loguru import logger

RAW_DIR = Path("data/raw")
