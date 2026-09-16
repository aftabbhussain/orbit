from backend.contracts import ThoughtRecord

def create_route_thought(route: str) -> ThoughtRecord:
    return ThoughtRecord(thought=f"Decided routing to {route}", action="router")
