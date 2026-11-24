import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class VectorDbConfig:
    host_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    auth_token: str | None = os.getenv("QDRANT_API_KEY", None)
    target_collection: str = os.getenv("QDRANT_COLLECTION", "arxiv_papers")

    @property
    def url(self) -> str:
        return self.host_url

    @property
    def api_key(self) -> str | None:
        return self.auth_token

    @property
    def collection(self) -> str:
        return self.target_collection


@dataclass(frozen=True)
class SearchEngineConfig:
    node_url: str = os.getenv("ES_URL", "http://localhost:9200")
    index_name: str = os.getenv("ES_INDEX", "arxiv_papers")

    @property
    def url(self) -> str:
        return self.node_url

    @property
    def index(self) -> str:
        return self.index_name


@dataclass(frozen=True)
class EncoderConfig:
    dense_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    dense_field_name: str = "dense"

    @property
    def dense_model(self) -> str:
        return self.dense_model_name

    @property
    def dense_vector_name(self) -> str:
        return self.dense_field_name


@dataclass(frozen=True)
class RerankConfig:
    model_identifier: str = os.getenv(
        "RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )
    max_candidates: int = int(os.getenv("RERANKER_TOP_K", "5"))

    @property
    def model(self) -> str:
        return self.model_identifier

    @property
    def top_k(self) -> int:
        return self.max_candidates


@dataclass(frozen=True)
class FusionConfig:
    constant_k: int = int(os.getenv("RRF_K", "60"))

    @property
    def rrf_k(self) -> int:
        return self.constant_k


@dataclass(frozen=True)
class AppSettings:
    qdrant: VectorDbConfig = field(default_factory=VectorDbConfig)
    elasticsearch: SearchEngineConfig = field(default_factory=SearchEngineConfig)
    embedding: EncoderConfig = field(default_factory=EncoderConfig)
    reranker: RerankConfig = field(default_factory=RerankConfig)
    hybrid_retrieval: FusionConfig = field(default_factory=FusionConfig)


settings = AppSettings()
