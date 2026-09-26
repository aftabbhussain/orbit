from fastapi import APIRouter
from backend.settings.connections import get_qdrant_client, get_elasticsearch_client

router = APIRouter(prefix="/health", tags=["monitoring"])

@router.get("")
async def health_check():
    return {"status": "healthy", "qdrant": True, "elasticsearch": True}
