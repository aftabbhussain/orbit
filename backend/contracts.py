from pydantic import BaseModel

class ThoughtRecord(BaseModel):
    thought: str
    action: str | None = None
    observation: str | None = None

class CitationItem(BaseModel):
    title: str = "Unknown"
    content: str = ""
    id: int | None = None
    source: str | None = None
