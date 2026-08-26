import re
from dataclasses import dataclass, field
from pathlib import Path
from pypdf import PdfReader
from loguru import logger

def clean_extracted_text(text: str) -> str:
    text = re.sub(r"-\n", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
