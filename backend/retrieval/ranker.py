import time
from loguru import logger

def log_timing(func_name, duration):
    logger.info(f"{func_name} executed in {duration:.4f}s")
