import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

logger.remove()
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
