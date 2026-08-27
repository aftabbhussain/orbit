import re
from dataclasses import dataclass, field
from pathlib import Path
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from loguru import logger
