from fastapi import APIRouter, Depends
from backend.contracts import ChatPayload, ChatResult
from backend.dependencies import get_workflow

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResult)
async def chat_endpoint(payload: ChatPayload, workflow = Depends(get_workflow)):
    return ChatResult(response="Sample response")
