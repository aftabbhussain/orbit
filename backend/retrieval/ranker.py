from sentence_transformers import CrossEncoder
from loguru import logger

reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
