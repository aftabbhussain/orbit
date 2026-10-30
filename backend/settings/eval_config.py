from pydantic_settings import BaseSettings

class EvalConfig(BaseSettings):
    benchmark_dataset: str = "data/test/test_queries.json"
    hit_rate_k: int = 5
    mrr_k: int = 10
