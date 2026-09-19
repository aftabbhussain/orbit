def build_grounded_prompt(query: str, citations: list) -> str:
    context_str = "\n\n".join([f"[{c.id}] {c.title}\n{c.content}" for c in citations])
    return f"Context:\n{context_str}\n\nQuestion: {query}\nAnswer:"
