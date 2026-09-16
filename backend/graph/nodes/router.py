from loguru import logger

def safe_parse_json(text: str) -> dict:
    try:
        import json
        return json.loads(text)
    except Exception:
        logger.warning("JSON parse failed, falling back to default route")
        return {"route": "knowledge_lookup"}
