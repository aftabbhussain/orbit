from langgraph.graph import StateGraph, END
from backend.graph.context import ConversationState
from backend.graph.nodes.router import router_node
from backend.graph.nodes.knowledge_lookup import knowledge_lookup_node
from backend.graph.nodes.live_web import live_web_node
from backend.graph.nodes.writer import writer_node
from backend.graph.nodes.judge import judge_node

def build_graph():
    builder = StateGraph(ConversationState)
    builder.add_node("router", router_node)
    builder.add_node("knowledge_lookup", knowledge_lookup_node)
    builder.add_node("live_web", live_web_node)
    builder.add_node("writer", writer_node)
    builder.add_node("judge", judge_node)
    return builder
