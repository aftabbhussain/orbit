from langgraph.graph import StateGraph, END
from backend.graph.context import ConversationState

def route_decision(state: ConversationState):
    return state.next_step
