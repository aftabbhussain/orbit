from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any

from elasticsearch import Elasticsearch
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client import models as qdrant_models

from backend.settings.connections import get_es_client, get_qdrant_client
from backend.settings.environment import settings


@dataclass
class RetrievedDocument:
    id: int
    content: str
    title: str
    score: float
    source: str
    metadata: dict[str, Any] | None = None


SearchResult = RetrievedDocument


@dataclass
class SearchParameters:
    prefetch_k: int = 50
    final_k: int = 20
    rrf_k: int = 60
    rerank_top_k: int = 5


RetrievalConfig = SearchParameters


class HybridIndex:
    _cached_cross_encoder = None
    _cached_embed_model = None

    def __init__(
        self,
        qdrant_client: QdrantClient | None = None,
        es_client: Elasticsearch | None = None,
        config: SearchParameters | None = None,
    ):
        self.qdrant = qdrant_client or get_qdrant_client()
        self.es = es_client or get_es_client()
        self.config = config or SearchParameters()
        self.rrf_k = self.config.rrf_k

    @classmethod
    def get_cross_encoder(cls):
        if cls._cached_cross_encoder is None:
            from sentence_transformers import CrossEncoder

            cls._cached_cross_encoder = CrossEncoder(settings.reranker.model)
        return cls._cached_cross_encoder

    @classmethod
    def get_embed_model(cls):
        if cls._cached_embed_model is None:
            from sentence_transformers import SentenceTransformer

            cls._cached_embed_model = SentenceTransformer(
                settings.embedding.dense_model
            )
        return cls._cached_embed_model

    def dense_search(self, query: str, top_k: int = 50) -> list[RetrievedDocument]:
        target_col = settings.qdrant.collection
        model_name = settings.embedding.dense_model
        vector_field = settings.embedding.dense_vector_name

        query_doc = qdrant_models.Document(text=query, model=model_name)
        response = self.qdrant.query_points(
            collection_name=target_col,
            query=query_doc,
            using=vector_field,
            limit=top_k,
            with_payload=True,
        )

        documents = []
        for point in response.points:
            payload = point.payload or {}
            doc_title = payload.get("title") or payload.get("section", "Unknown")
            documents.append(
                RetrievedDocument(
                    id=int(point.id),
                    content=payload.get("content", ""),
                    title=doc_title,
                    score=point.score or 0.0,
                    source="dense",
                    metadata=payload,
                )
            )
        return documents

    def bm25_search(self, query: str, top_k: int = 50) -> list[RetrievedDocument]:
        es_query = {
            "multi_match": {
                "query": query,
                "fields": ["title^3.0", "content^2.0"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        }
        res = self.es.search(
            index=settings.elasticsearch.index, query=es_query, size=top_k
        )
        hits = res.get("hits", {}).get("hits", [])

        results = []
        for hit in hits:
            source_data = hit.get("_source", {})
            results.append(
                RetrievedDocument(
                    id=int(hit["_id"]),
                    content=source_data.get("content", ""),
                    title=source_data.get("title", "Unknown"),
                    score=float(hit["_score"]),
                    source="bm25",
                    metadata=source_data,
                )
            )
        return results

    def rrf_fuse(
        self, result_lists: list[list[RetrievedDocument]], top_k: int = 20
    ) -> list[RetrievedDocument]:
        accumulated_scores: dict[int, float] = {}
        doc_store: dict[int, RetrievedDocument] = {}
        smooth_k = self.rrf_k

        for doc_list in result_lists:
            for rank_index, item in enumerate(doc_list, start=1):
                doc_store[item.id] = item
                current = accumulated_scores.get(item.id, 0.0)
                accumulated_scores[item.id] = current + (1.0 / (smooth_k + rank_index))

        ranked_pairs = sorted(
            accumulated_scores.items(), key=lambda pair: pair[1], reverse=True
        )
        return [doc_store[doc_id] for doc_id, _ in ranked_pairs[:top_k]]

    def search(
        self, query: str, top_k: int | None = None, prefetch: int | None = None
    ) -> list[RetrievedDocument]:
        cleaned = query.strip() if query else ""
        if not cleaned:
            return []

        limit = top_k or self.config.final_k
        initial_pool = prefetch or self.config.prefetch_k

        try:
            dense_docs = self.dense_search(cleaned, top_k=initial_pool)
            bm25_docs = self.bm25_search(cleaned, top_k=initial_pool)
            fused = self.rrf_fuse([dense_docs, bm25_docs], top_k=self.config.final_k)
            return self.rerank(cleaned, fused, limit)
        except Exception as exc:
            logger.error(f"[Ranker] Retrieval error: {exc}")
            return []

    def rerank(
        self, query: str, docs: list[RetrievedDocument], top_k: int | None = None
    ) -> list[RetrievedDocument]:
        target_k = top_k or self.config.rerank_top_k
        if not docs:
            return []

        try:
            model = self.get_cross_encoder()
        except Exception as exc:
            logger.warning(f"[Ranker] CrossEncoder fallback: {exc}")
            return docs[:target_k]

        text_pairs = [(query, f"{d.title}. {d.content}"[:1000]) for d in docs]
        scores = model.predict(text_pairs)

        paired = list(zip(docs, scores))
        paired.sort(key=lambda t: float(t[1]), reverse=True)

        return [d for d, _ in paired[:target_k]]


VectorSearch = HybridIndex


class WebSearch:
    def __init__(self, api_key: str | None = None, max_results: int = 5):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.max_results = max_results
        self.client = None

        if self.api_key:
            try:
                from tavily import TavilyClient

                self.client = TavilyClient(api_key=self.api_key)
            except ImportError:
                pass

    def is_available(self) -> bool:
        return self.client is not None

    def search(self, query: str) -> list[RetrievedDocument]:
        if not query or not query.strip():
            return []
        if not self.client:
            return []

        try:
            resp = self.client.search(
                query=query.strip(), max_results=self.max_results
            )
            raw_results = resp.get("results", [])

            output = []
            for idx, r in enumerate(raw_results):
                output.append(
                    RetrievedDocument(
                        id=idx,
                        content=r.get("content", ""),
                        title=r.get("title", "Web Result"),
                        score=r.get("score", 0.0),
                        source="web",
                        metadata={"url": r.get("url", "")},
                    )
                )
            return output
        except Exception as err:
            logger.error(f"[WebSearch] Error occurred: {err}")
            return []
