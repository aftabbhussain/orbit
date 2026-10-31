def compute_hit_rate(retrieved: list[str], ground_truth: list[str], k: int = 5) -> float:
    top_k = retrieved[:k]
    return 1.0 if any(gt in top_k for gt in ground_truth) else 0.0

def compute_mrr(retrieved: list[str], ground_truth: list[str]) -> float:
    for rank, item in enumerate(retrieved):
        if item in ground_truth:
            return 1.0 / (rank + 1)
    return 0.0
