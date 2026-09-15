from dataclasses import dataclass, field, replace
from backend.contracts import ThoughtRecord, CitationItem

def copy_state(state: ConversationState, **kwargs) -> ConversationState:
    return replace(state, **kwargs)
