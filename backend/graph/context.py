from dataclasses import dataclass, field
from backend.contracts import ThoughtRecord, CitationItem

@dataclass
class ConversationState:
    query: str
    messages: list[dict] = field(default_factory=list)
    thoughts: list[ThoughtRecord] = field(default_factory=list)
    citations: list[CitationItem] = field(default_factory=list)
    answer: str = ""
