from fastapi import APIRouter
from backend.contracts import ChatPayload, ChatResult

router = APIRouter(prefix="/chat", tags=["chat"])
