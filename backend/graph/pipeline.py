from dataclasses import dataclass

@dataclass
class WorkflowOutcome:
    answer: str = ""
    citations: list = None
    thoughts: list = None
