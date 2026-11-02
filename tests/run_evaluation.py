#!/usr/bin/env python3

import asyncio
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).parent.parent.resolve()
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import requests
from tqdm import tqdm
from backend.metrics.benchmark import RagasBenchmarkRunner

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
CHAT_URL = f"{BASE_URL}/api/chat"
TIMEOUT_LIMIT = 500
CONCURRENCY_WORKERS = 5


def read_evaluation_corpus(
    filepath: str = "data/test/test_queries.json",
) -> list[dict[str, Any]]:
    loc = PROJECT_DIR / filepath
    with open(loc, "r", encoding="utf-8") as stream:
        payload = json.load(stream)
    return payload["queries"]


def call_chat_endpoint(prompt: str, session_key: str | None = None) -> dict[str, Any]:
    body = {"message": prompt}
    if session_key:
        body["session_id"] = session_key

    resp = requests.post(CHAT_URL, json=body, timeout=TIMEOUT_LIMIT)
    resp.raise_for_status()
    return resp.json()


async def score_sample_async(
    evaluator: RagasBenchmarkRunner,
    query: str,
    answer: str,
    contexts: list[str],
    reference: str | None,
) -> dict[str, Any]:
    eval_record = await evaluator.evaluate_sample(
        query=query,
        answer=answer,
        contexts=contexts,
        reference=reference,
    )
    return {
        "faithfulness": eval_record.scores.get("faithfulness"),
        "answer_relevancy": eval_record.scores.get("answer_relevancy"),
        "context_precision": eval_record.scores.get("context_precision"),
        "answer_similarity": eval_record.scores.get("answer_similarity"),
        "total_score": eval_record.total_score,
    }


def execute_query_assessment(sample: dict[str, Any]) -> dict[str, Any]:
    record = {
        "query_id": sample["id"],
        "query": sample["query"],
        "expected_paper_ids": sample.get("expected", {}).get("paper_ids", []),
        "ragas_metrics": {
            "faithfulness": None,
            "answer_relevancy": None,
            "context_precision": None,
            "answer_similarity": None,
            "total_score": None,
        },
        "api_response": None,
        "error": None,
    }

    query_str = sample["query"]
    target_data = sample.get("expected", {})
    ideal_response = target_data.get("answer")

    try:
        api_data = call_chat_endpoint(query_str, session_key=f"eval-{sample['id']}")
        record["api_response"] = {
            "answer": api_data.get("answer", ""),
            "sources_count": len(api_data.get("sources", [])),
        }

        docs = api_data.get("sources", [])
        contexts = [d.get("content", "") for d in docs if d.get("content")]

        if contexts and api_data.get("answer"):
            try:
                evaluator_instance = RagasBenchmarkRunner()
                scored_data = asyncio.run(
                    score_sample_async(
                        evaluator=evaluator_instance,
                        query=query_str,
                        answer=api_data["answer"],
                        contexts=contexts,
                        reference=ideal_response,
                    )
                )
                record["ragas_metrics"] = scored_data
            except Exception as err:
                record["error"] = f"Evaluation failure: {str(err)}"

    except requests.exceptions.Timeout:
        record["error"] = "Timeout"
    except requests.exceptions.RequestException as exc:
        record["error"] = f"Request error: {str(exc)}"
    except Exception as unk:
        record["error"] = f"Unexpected failure: {str(unk)}"

    return record


def compile_metrics_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    metric_keys = [
        "faithfulness",
        "answer_relevancy",
        "context_precision",
        "answer_similarity",
        "total_score",
    ]

    issue_list = [r["error"] for r in results if r["error"]]
    timeout_total = sum(1 for e in issue_list if e == "Timeout")

    metrics_map = {}
    for key in metric_keys:
        collected = [
            r["ragas_metrics"].get(key)
            for r in results
            if r["ragas_metrics"].get(key) is not None
        ]
        metrics_map[key] = {
            "mean": round(sum(collected) / len(collected), 4) if collected else None,
            "count": len(collected),
        }

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_queries": len(results),
        },
        "ragas_metrics": metrics_map,
        "errors": {
            "total": len(issue_list),
            "timeout": timeout_total,
            "details": issue_list[:10],
        },
    }


def main():
    print("=" * 60)
    print("Benchmark Assessment Suite")
    print("=" * 60)

    try:
        dataset = read_evaluation_corpus()
    except Exception as exc:
        print(f"[ERROR] Could not load queries: {exc}")
        sys.exit(1)

    print(f"\n[Step 1] Loaded {len(dataset)} queries from corpus")

    print("\n[Step 2] Testing server connectivity...")
    try:
        probe = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if probe.status_code == 200:
            print(f"  [OK] Server is reachable at {BASE_URL}")
        else:
            print(f"  [WARN] Server responded with code {probe.status_code}")
    except requests.exceptions.RequestException as exc:
        print(f"  [FAIL] Unable to connect: {exc}")
        sys.exit(1)

    print("\n[Step 3] Processing query evaluations...")
    results_list = []

    with ThreadPoolExecutor(max_workers=CONCURRENCY_WORKERS) as pool:
        future_map = {
            pool.submit(execute_query_assessment, sample): sample for sample in dataset
        }
        with tqdm(total=len(dataset), desc="Progress", unit="query") as bar:
            for fut in as_completed(future_map):
                try:
                    res = fut.result()
                    results_list.append(res)
                except Exception as exc:
                    item = future_map[fut]
                    results_list.append(
                        {
                            "query_id": item["id"],
                            "query": item["query"],
                            "error": f"Execution error: {str(exc)}",
                        }
                    )
                bar.update(1)

    print("\n[Step 4] Summarizing results...")
    summary_data = compile_metrics_summary(results_list)

    out_folder = PROJECT_DIR / "tests"
    out_folder.mkdir(parents=True, exist_ok=True)

    details_dest = out_folder / "evaluation_results.json"
    with open(details_dest, "w", encoding="utf-8") as stream:
        json.dump(results_list, stream, indent=2, ensure_ascii=False)
    print(f"  [INFO] Detailed scores saved to {details_dest}")

    summary_dest = out_folder / "evaluation_summary.json"
    with open(summary_dest, "w", encoding="utf-8") as stream:
        json.dump(summary_data, stream, indent=2, ensure_ascii=False)
    print(f"  [INFO] Overall summary saved to {summary_dest}")

    print("\n" + "=" * 60)
    print("EVALUATION FINISHED")
    print("=" * 60)
    print(f"Total processed: {summary_data['summary']['total_queries']}")

    for k, v in summary_data["ragas_metrics"].items():
        if v["mean"] is not None:
            print(f"  {k}: {v['mean']:.4f} (count: {v['count']})")

    if summary_data["errors"]["total"] > 0:
        print(f"  Errors encountered: {summary_data['errors']['total']}")


if __name__ == "__main__":
    main()
