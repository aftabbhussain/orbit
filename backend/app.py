from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing system dependencies")
    yield
    logger.info("Tearing down services")
