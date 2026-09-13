from pydantic import BaseModel, Field


class ThoughtRecord(BaseModel):
    thought: str
    action: str | None = None
    observation: str | None = None


class CitationItem(BaseModel):
    title: str = "Unknown"
    content: str = ""
    id: int | None = None
    score: float | None = None
    source: str | None = None
    metadata: dict | None = None


class ChatPayload(BaseModel):
    message: str = Field(..., description="User message", min_length=1)
    session_id: str | None = Field(
        None, description="Session ID for conversation continuity"
    )


class ChatResult(BaseModel):
    answer: str = Field(..., description="Agent's response")
    session_id: str = Field(..., description="Session ID")
    reasoning_steps: list[ThoughtRecord] = Field(default_factory=list)
    sources: list[CitationItem] = Field(default_factory=list)
    execution_time: float = Field(..., description="Execution time in milliseconds")
    node_timings: dict | None = None


class SystemStatus(BaseModel):
    status: str
    version: str
    components: dict[str, str]


ReasoningStep = ThoughtRecord
Source = CitationItem
ChatRequest = ChatPayload
ChatResponse = ChatResult
HealthCheck = SystemStatus
