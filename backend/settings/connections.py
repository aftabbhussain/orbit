import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient

from backend.settings.environment import settings

load_dotenv()


def get_llm_client() -> ChatOpenAI:
    token_limit = int(os.getenv("NVIDIA_NIM_MAX_TOKENS", "2048"))
    model_name = os.getenv("NVIDIA_NIM_MODEL", "minimaxai/minimax-m3.1-flash")
    endpoint = os.getenv(
        "NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1"
    )
    api_key = os.getenv("NVIDIA_NIM_API_KEY", "")

    return ChatOpenAI(
        api_key=api_key,
        base_url=endpoint,
        model=model_name,
        temperature=0.7,
        max_tokens=token_limit,
    )


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant.host_url,
        api_key=settings.qdrant.auth_token,
    )


def get_es_client() -> Elasticsearch:
    return Elasticsearch(settings.elasticsearch.node_url, request_timeout=60)
