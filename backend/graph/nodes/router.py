import json
from loguru import logger
from backend.graph.context import ConversationState

def parse_route(raw_text: str) -> str:
    if "LIVE_WEB" in raw_text:
        return "live_web"
    return "knowledge_lookup"
