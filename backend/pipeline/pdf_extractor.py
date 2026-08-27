import re
from dataclasses import dataclass, field
from pathlib import Path
from pypdf import PdfReader
from loguru import logger

def extract_arxiv_id(file_path: Path) -> str:
    stem = file_path.stem
    match = re.search(r"(\d{4}\.\d{4,5})", stem)
    return match.group(1) if match else stem
