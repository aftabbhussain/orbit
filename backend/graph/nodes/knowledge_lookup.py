from backend.contracts import CitationItem

def format_citations(results: list[dict]) -> list[CitationItem]:
    items = []
    for i, res in enumerate(results):
        items.append(CitationItem(id=i+1, title=res.get("title", ""), content=res.get("content", "")))
    return items
