from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["monitoring"])

@router.get("")
async def health_check():
    return {"status": "ok"}
