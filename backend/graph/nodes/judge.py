from backend.contracts import ThoughtRecord

def route_critique(score: float) -> str:
    if score < 0.7:
        return "retry_retrieval"
    return "finish"
