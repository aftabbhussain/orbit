from dataclasses import dataclass

@dataclass
class EvaluationSummary:
    total_queries: int = 0
    hit_rate_at_5: float = 0.0
    mrr: float = 0.0
    faithfulness: float = 0.0
