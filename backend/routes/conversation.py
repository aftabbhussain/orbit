from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/chat", tags=["chat"])

async def event_generator():
    yield "data: {}\n\n"
