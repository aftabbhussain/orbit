from langfuse.langchain import CallbackHandler
from loguru import logger

def get_tracer():
    return CallbackHandler()
