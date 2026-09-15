from typing import TypedDict, Annotated, Literal, Optional
import operator


class ConversationMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str
    timestamp: Optional[str]


Message = ConversationMessage


class ConversationState(TypedDict):
    query: str
    decision: Literal["direct_answer", "reject", "clarify", "process"]
    route: Optional[Literal["vector_search", "web_search"]]
    document: list[dict]
    validation_result: Optional[Literal["relevant", "insufficient", "off_topic"]]
    answer: str
    source: list[dict]
    reasoning_step: Annotated[list[str], operator.add]
    chat_history: Annotated[list[ConversationMessage], operator.add]
    node_timings: dict


AgentState = ConversationState
