from collections import defaultdict

def reciprocal_rank_fusion(dense_ranks, bm25_ranks, k: int = 60):
    scores = defaultdict(float)
    for rank, doc_id in enumerate(dense_ranks):
        scores[doc_id] += 1.0 / (k + rank + 1)
    for rank, doc_id in enumerate(bm25_ranks):
        scores[doc_id] += 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
