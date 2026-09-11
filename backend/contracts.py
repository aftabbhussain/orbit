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
    message: str = Field(..., description="User message")
    session_id: str | None = None
