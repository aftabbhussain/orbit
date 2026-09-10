def truncate_text(text: str, max_chars: int = 2000) -> str:
    return text[:max_chars] if len(text) > max_chars else text
