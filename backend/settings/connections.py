from loguru import logger
from backend.settings.environment import get_settings

class ConnectionManager:
    def __init__(self):
        self._qdrant = None
        self._es = None
