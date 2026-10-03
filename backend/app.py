from fastapi import FastAPI
from backend.routes.conversation import router as chat_router
from backend.routes.monitoring import router as health_router

app = FastAPI(title="Academic Research Assistant API")
app.include_router(chat_router)
app.include_router(health_router)
