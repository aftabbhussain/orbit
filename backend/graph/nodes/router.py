import re
from loguru import logger

def extract_keywords(query: str) -> list[str]:
    words = re.findall(r"\w+", query.lower())
    return [w for w in words if len(w) > 3]
