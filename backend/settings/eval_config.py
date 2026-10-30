from pydantic_settings import BaseSettings

class EvalConfig(BaseSettings):
    benchmark_dataset: str = "data/test/test_queries.json"
    hit_rate_k: int = 5
    mrr_k: int = 10
    min_faithfulness_score: float = 0.85
    min_citation_precision: float = 0.80
