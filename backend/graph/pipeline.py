from langgraph.graph import StateGraph, END
from backend.graph.context import ConversationState

def build_graph():
    builder = StateGraph(ConversationState)
    return builder
