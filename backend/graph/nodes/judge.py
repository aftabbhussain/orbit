import time
from typing import Literal

from loguru import logger
from pydantic import BaseModel

from backend.graph.context import ConversationState
from backend.settings.connections import get_llm_client
from backend.settings.prompts import VALIDATE_HUMAN_TEMPLATE, VALIDATE_SYSTEM_PROMPT


class RelevanceVerdict(BaseModel):
    validation: Literal["relevant", "insufficient", "off_topic"]
    reasoning: str


ValidationOutcome = RelevanceVerdict


def validation_node(state: ConversationState) -> dict:
    query = state.get("query", "")
    documents = state.get("document", [])
    prior_timings = state.get("node_timings", {})

    if not documents:
        logger.info("[Judge] Document list is empty")
        return {
            "document": documents,
            "validation_result": "insufficient",
            "reasoning_step": ["VALIDATE: No documents found"],
            "node_timings": prior_timings,
        }

    client = get_llm_client()
    if not client:
        logger.warning("[Judge] LLM client missing, treating as relevant")
        return {
            "document": documents,
            "validation_result": "relevant",
            "reasoning_step": ["VALIDATE: No LLM, assuming relevant"],
            "node_timings": prior_timings,
        }

    formatted_docs = "\n".join(
        f"[{idx + 1}] {d.get('title', 'Unknown')}: {d.get('content', '')[:500]}"
        for idx, d in enumerate(documents[:3])
    )

    prompt_messages = [
        {"role": "system", "content": VALIDATE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": VALIDATE_HUMAN_TEMPLATE.format(
                query=query, documents=formatted_docs
            ),
        },
    ]

    start_time = time.time()
    try:
        grader = client.with_structured_output(RelevanceVerdict)
        eval_result = grader.invoke(prompt_messages)
        duration = (time.time() - start_time) * 1000
        new_timings = {**prior_timings, "validate": duration}

        if isinstance(eval_result, dict):
            eval_result = RelevanceVerdict(**eval_result)

        logger.info(
            f"[Judge] Status: {eval_result.validation} - {eval_result.reasoning}"
        )
        return {
            "document": documents,
            "validation_result": eval_result.validation,
            "reasoning_step": [
                f"VALIDATE: {eval_result.validation} - {eval_result.reasoning}"
            ],
            "node_timings": new_timings,
        }

    except Exception as exc:
        logger.error(f"[Judge] Evaluation encountered error: {exc}")
        return {
            "document": documents,
            "validation_result": "relevant",
            "reasoning_step": [
                f"VALIDATE: Error occurred ({exc}), defaulting to relevant"
            ],
            "node_timings": prior_timings,
        }


relevance_judge_node = validation_node
