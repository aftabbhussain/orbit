from backend.contracts import ThoughtRecord

def record_retrieval_thought(count: int) -> ThoughtRecord:
    return ThoughtRecord(thought=f"Retrieved {count} relevant paper chunks from arXiv index", action="knowledge_lookup")
