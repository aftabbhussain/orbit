def filter_by_score(candidates, min_score: float = 0.15):
    return [c for c in candidates if c.get("score", 0) >= min_score]
