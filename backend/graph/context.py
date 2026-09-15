from dataclasses import dataclass, field

@dataclass
class ConversationState:
    query: str
    messages: list[dict] = field(default_factory=list)
