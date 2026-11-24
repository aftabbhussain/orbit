import time
import uuid
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from backend.contracts import ChatPayload, ChatResult, ThoughtRecord, CitationItem
from backend.dependencies import get_workflow
from backend.graph.pipeline import MultiAgentWorkflow, WorkflowOutcome

router = APIRouter(prefix="/chat", tags=["chat"])

STEP_DISPATCH = {
    "PLANNER:": ("planner", "Query analyzed"),
    "VECTOR_SEARCH:": ("vector_search", "Searching arXiv papers"),
    "WEB_SEARCH:": ("web_search", "Searching the web"),
    "VALIDATE:": ("validate", "Document validated"),
    "GEN:": ("generate", "Answer generated"),
    "ERROR:": ("error", "Error occurred"),
}


def new_session_token() -> str:
    return str(uuid.uuid4())


def parse_citations(items: list[dict]) -> list[CitationItem]:
    return [CitationItem.model_validate(c) for c in items]


def extract_thought_sequence(outcome: WorkflowOutcome) -> list[ThoughtRecord]:
    chain = []
    seen = set()

    for entry in outcome.reasoning_step:
        if entry in seen:
            continue
        seen.add(entry)

        matched = False
        for prefix, (action_name, fallback_obs) in STEP_DISPATCH.items():
            if entry.startswith(prefix):
                observation = entry if action_name == "retrieve" else fallback_obs
                chain.append(
                    ThoughtRecord(
                        thought=entry,
                        action=action_name,
                        observation=observation,
                    )
                )
                matched = True
                break

        if not matched:
            chain.append(ThoughtRecord(thought=entry, action="step", observation=""))

    return chain


@router.post("", response_model=ChatResult)
async def handle_chat_message(
    payload: ChatPayload,
    pipeline: MultiAgentWorkflow = Depends(get_workflow),
) -> ChatResult:
    session_id = payload.session_id or new_session_token()
    logger.info(
        f"[ChatRoute] Session {session_id} - Prompt: {payload.message[:50]}..."
    )

    t0 = time.time()
    try:
        outcome: WorkflowOutcome = pipeline.run(
            payload.message, session_id=session_id
        )
        total_time_ms = (time.time() - t0) * 1000

        return ChatResult(
            answer=outcome.answer,
            session_id=session_id,
            reasoning_steps=extract_thought_sequence(outcome),
            sources=parse_citations(outcome.source),
            execution_time=total_time_ms,
            node_timings=outcome.node_timings,
        )

    except Exception as exc:
        logger.error(f"[ChatRoute] Request processing failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to process request: {str(exc)}"
        )


@router.get("/history/{session_id}")
async def fetch_session_history(session_id: str):
    return {"session_id": session_id, "messages": []}


@router.delete("/session/{session_id}")
async def clear_session_history(session_id: str):
    return {"status": "cleared", "session_id": session_id}
