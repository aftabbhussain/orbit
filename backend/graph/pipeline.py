from __future__ import annotations
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from langfuse.langchain import CallbackHandler
from langgraph.errors import GraphRecursionError, NodeInterrupt
from langgraph.graph import END, StateGraph
from loguru import logger

from backend.graph.context import ConversationState
from backend.graph.nodes.judge import validation_node
from backend.graph.nodes.knowledge_lookup import vector_search_node
from backend.graph.nodes.live_web import web_search_node
from backend.graph.nodes.router import plan_node
from backend.graph.nodes.writer import gen_node


@dataclass
class WorkflowOutcome:
    answer: str
    source: list[dict] = field(default_factory=list)
    reasoning_step: list[str] = field(default_factory=list)
    node_timings: dict = field(default_factory=dict)
    trace_id: str | None = None
    langfuse_url: str | None = None


ExecutionResult = WorkflowOutcome


def route_question(state: ConversationState) -> str:
    decision = state.get("decision")
    route = state.get("route")
    logger.info(f"[Router] Decision={decision}, route={route}")

    if decision in ["direct_answer", "reject", "clarify"]:
        return "generate"
    if decision == "process":
        if route == "web_search":
            return "web_search"
        return "vector_search"

    logger.warning("[Router] Unrecognized state, defaulting to generate")
    return "generate"


def decide_to_generate(state: ConversationState) -> str:
    validation = state.get("validation_result")
    logger.info(f"[Router] Evaluation verdict: {validation}")

    if validation == "relevant":
        return "generate"

    logger.info(f"[Router] Relevance is {validation}, diverting to web search")
    return "web_search"


class MultiAgentWorkflow:
    def __init__(self):
        self.app = self.create_and_compile_graph()

    def create_and_compile_graph(self):
        graph = StateGraph(ConversationState)

        graph.add_node("planner", plan_node)
        graph.add_node("vector_search", vector_search_node)
        graph.add_node("validate", validation_node)
        graph.add_node("web_search", web_search_node)
        graph.add_node("generate", gen_node)

        graph.set_entry_point("planner")

        graph.add_conditional_edges(
            "planner",
            route_question,
            {
                "generate": "generate",
                "vector_search": "vector_search",
                "web_search": "web_search",
            },
        )

        graph.add_edge("vector_search", "validate")
        graph.add_conditional_edges(
            "validate",
            decide_to_generate,
            {
                "generate": "generate",
                "web_search": "web_search",
            },
        )

        graph.add_edge("web_search", "generate")
        graph.add_edge("generate", END)

        return graph.compile()

    def run(self, query: str, session_id: str | None = None) -> WorkflowOutcome:
        thread_id = session_id or str(uuid.uuid4())

        initial_state: ConversationState = {
            "query": query,
            "decision": "process",
            "route": None,
            "document": [],
            "validation_result": None,
            "answer": "",
            "source": [],
            "reasoning_step": [],
            "chat_history": [
                {
                    "role": "user",
                    "content": query,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
            "node_timings": {},
        }

        callbacks = []
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            try:
                callbacks.append(CallbackHandler())
            except Exception as err:
                logger.warning(f"Could not initialize Langfuse callback: {err}")

        try:
            result = self.app.invoke(
                initial_state,
                config={
                    "configurable": {"thread_id": thread_id},
                    "recursion_limit": 10,
                    "callbacks": callbacks,
                },
            )
        except NodeInterrupt as interrupt:
            logger.error(f"[Workflow] Graph interrupted: {interrupt}")
            return WorkflowOutcome(
                answer="Service temporarily unavailable",
                source=[],
                reasoning_step=[f"INTERRUPT: {interrupt}"],
            )
        except GraphRecursionError as rec_err:
            logger.error(f"[Workflow] Max recursion reached: {rec_err}")
            return WorkflowOutcome(
                answer="Service temporarily unavailable",
                source=[],
                reasoning_step=[f"RECURSION_ERROR: {rec_err}"],
            )
        except Exception as unexpected_err:
            logger.exception(f"[Workflow] Unhandled error: {unexpected_err}")
            return WorkflowOutcome(
                answer="Service temporarily unavailable",
                source=[],
                reasoning_step=[f"ERROR: {str(unexpected_err)}"],
            )

        return WorkflowOutcome(
            answer=result.get("answer", ""),
            source=result.get("source", []),
            reasoning_step=result.get("reasoning_step", []),
            node_timings=result.get("node_timings", {}),
        )


ResearchPipeline = MultiAgentWorkflow


def create_workflow() -> MultiAgentWorkflow:
    return MultiAgentWorkflow()
