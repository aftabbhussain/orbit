import re
from dataclasses import dataclass, field
from pathlib import Path
from pypdf import PdfReader
from loguru import logger

SECTION_PATTERNS = [
    r"^(?:abstract|introduction|related work|background|methodology|methods|experiments|results|discussion|conclusion|references)\b"
]
