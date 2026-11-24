import time
import uuid
from typing import Literal, Optional

from langgraph.errors import NodeInterrupt
from loguru import logger
from pydantic import BaseModel

from backend.graph.context import ConversationState
from backend.settings.connections import get_llm_client
from backend.settings.prompts import PLANNER_PROMPT_TEMPLATE


class RouteDecision(BaseModel):
    decision: Literal["direct_answer", "reject", "clarify", "process"]
    route: Optional[Literal["vector_search", "web_search"]] = None
    reasoning: str


PlannerOutcome = RouteDecision


def plan_node(state: ConversationState) -> dict:
    call_id = str(uuid.uuid4())[:8]
    query_text = state["query"]
    prev_timings = state.get("node_timings", {})

    logger.info(f"[Planner] Inspecting query [{call_id}]: {query_text[:50]}...")

    llm = get_llm_client()
    if not llm:
        raise NodeInterrupt("Service temporarily unavailable", id="planner")

    start_ts = time.time()
    try:
        classifier = llm.with_structured_output(RouteDecision)
        decision = classifier.invoke(
            PLANNER_PROMPT_TEMPLATE.invoke({"query": query_text})
        )
        elapsed_ms = (time.time() - start_ts) * 1000
        timings = {**prev_timings, "planner": elapsed_ms}

        if isinstance(decision, dict):
            decision = RouteDecision(**decision)

        if decision.decision in ["direct_answer", "reject", "clarify"]:
            return {
                "decision": decision.decision,
                "route": None,
                "reasoning_step": [
                    f"PLANNER: {decision.decision} - routing to generator (id={call_id})"
                ],
                "node_timings": timings,
            }

        if decision.decision == "process":
            chosen_route = decision.route or "vector_search"
            return {
                "decision": "process",
                "route": chosen_route,
                "reasoning_step": [
                    f"PLANNER: {decision.reasoning} - routing to {chosen_route}"
                ],
                "node_timings": timings,
            }

        return {
            "decision": "process",
            "route": "vector_search",
            "reasoning_step": ["PLANNER: Default routing to vector_search"],
            "node_timings": timings,
        }

    except Exception as err:
        logger.error(f"[Planner] Classification failed: {err}")
        return {
            "decision": "direct_answer",
            "route": None,
            "reasoning_step": [
                f"PLANNER: Error occurred ({err}), defaulting to direct answer"
            ],
            "node_timings": prev_timings,
        }


route_intent_node = plan_node
