import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.graph.pipeline import MultiAgentWorkflow
from backend.routes.conversation import router as chat_router
from backend.routes.monitoring import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Assistant API backend...")
    try:
        app.state.workflow = MultiAgentWorkflow()
        logger.info("Agent workflow ready")
    except Exception as exc:
        logger.error(f"Failed to initialize workflow: {exc}")
    yield
    logger.info("Stopping Assistant API backend...")


app = FastAPI(
    title="arXiv Research Assistant API",
    description="API for querying arXiv papers using RAG and ReAct agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(health_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "arXiv Research Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api")
async def api_info():
    return {
        "name": "arXiv Research Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "chat_stream": "/api/chat/stream",
            "health": "/api/health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
