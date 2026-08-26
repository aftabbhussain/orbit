from dataclasses import dataclass, field
from pathlib import Path
from pypdf import PdfReader
from loguru import logger

@dataclass
class PaperMetadata:
    arxiv_id: str
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
