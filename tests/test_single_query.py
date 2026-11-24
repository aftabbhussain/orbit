#!/usr/bin/env python3

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import requests
from backend.metrics.benchmark import RagasBenchmarkRunner

API_HOST = os.getenv("API_URL", "http://localhost:8000")
CHAT_ENDPOINT = f"{API_HOST}/api/chat"
TIMEOUT_SECS = 120


def read_first_benchmark(filepath: str = "data/test_queries.json") -> dict:
    target_path = project_root / filepath
    with open(target_path, "r", encoding="utf-8") as stream:
        content = json.load(stream)
    return content["queries"][0]


def send_chat_query(prompt: str) -> dict:
    resp = requests.post(CHAT_ENDPOINT, json={"message": prompt}, timeout=TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()


async def evaluate_output_async(
    evaluator: RagasBenchmarkRunner,
    query: str,
    answer: str,
    contexts: list[str],
    reference: str | None,
) -> dict[str, Any]:
    res = await evaluator.evaluate_sample(
        query=query,
        answer=answer,
        contexts=contexts,
        reference=reference,
    )
    return {
        "faithfulness": res.scores.get("faithfulness"),
        "answer_relevancy": res.scores.get("answer_relevancy"),
        "context_precision": res.scores.get("context_precision"),
        "answer_similarity": res.scores.get("answer_similarity"),
        "total_score": res.total_score,
    }


def main():
    print("=" * 60)
    print("Single Query Diagnostic Run")
    print("=" * 60)

    try:
        sample = read_first_benchmark()
    except Exception as err:
        print(f"[ERROR] Could not load sample queries: {err}")
        return

    sample_id = sample.get("id")
    query_text = sample.get("query", "")
    expected = sample.get("expected", {})
    expected_ids = expected.get("paper_ids", [])
    ref_answer = expected.get("answer")

    print(f"\nQuery ID: {sample_id}")
    print(f"Query: {query_text}")
    print(f"Expected IDs: {expected_ids}")

    print("\n[Step 1] Calling backend chat endpoint...")
    try:
        api_res = send_chat_query(query_text)
        answer = api_res.get("answer", "")
        sources = api_res.get("sources", [])

        print(f"  [OK] Answer received ({len(answer)} chars)")
        print(f"  [OK] Sources returned: {len(sources)}")
    except requests.exceptions.RequestException as exc:
        print(f"  [FAIL] Connection error: {exc}")
        return

    print("\n[Step 2] Running RAGAS evaluation...")
    contexts = [s.get("content", "") for s in sources if s.get("content")]

    try:
        runner = RagasBenchmarkRunner()
        metrics = asyncio.run(
            evaluate_output_async(
                evaluator=runner,
                query=query_text,
                answer=answer,
                contexts=contexts,
                reference=ref_answer,
            )
        )

        if metrics.get("faithfulness") is not None:
            print(f"  [OK] Faithfulness: {metrics['faithfulness']:.4f}")
            print(f"  [OK] Answer Relevancy: {metrics['answer_relevancy']:.4f}")
            if metrics.get("context_precision") is not None:
                print(f"  [OK] Context Precision: {metrics['context_precision']:.4f}")
            print(f"  [OK] Total Score: {metrics['total_score']:.4f}")
        else:
            print("  [WARN] Evaluation produced empty metrics")

    except Exception as exc:
        print(f"  [ERROR] Evaluation error: {exc}")

    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
