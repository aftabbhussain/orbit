import asyncio
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from dotenv import dotenv_values
from openai import AsyncOpenAI
from ragas.embeddings.base import embedding_factory
from ragas.llms import llm_factory
from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    SemanticSimilarity,
)
from loguru import logger


def read_llm_config() -> Dict[str, str]:
    config_vals = dotenv_values(".env")
    return {
        "api_key": config_vals.get("NVIDIA_NIM_API_KEY", ""),
        "base_url": config_vals.get(
            "NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1"
        ),
        "model": config_vals.get(
            "NVIDIA_NIM_MODEL", "meta/llama-3.3-70b-instruct"
        ),
    }


def init_eval_llm():
    cfg = read_llm_config()
    if not cfg["api_key"]:
        raise ValueError("NVIDIA_NIM_API_KEY not configured")

    client = AsyncOpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])
    llm_instance = llm_factory(
        cfg["model"],
        provider="openai",
        client=client,
        temperature=0.0,
        max_tokens=8192,
    )
    logger.info(f"RAGAS evaluation LLM initialized: {cfg['model']}")
    return llm_instance


def init_eval_embeddings():
    embed_name = os.getenv(
        "RAGAS_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    embeddings = embedding_factory(provider="huggingface", model=embed_name)
    logger.info(f"RAGAS embedding model loaded: {embed_name}")
    return embeddings


@dataclass
class EvaluationSampleRecord:
    query: str
    answer: str
    contexts: List[str]
    scores: Dict[str, float]
    total_score: float


RAGASEvaluationResult = EvaluationSampleRecord


@dataclass
class AggregatedMetrics:
    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    context_precision: float = 0.0
    answer_similarity: float = 0.0
    total_score: float = 0.0


EvaluationMetrics = AggregatedMetrics


class RagasBenchmarkRunner:
    def __init__(self):
        self.llm = init_eval_llm()
        self.embeddings = init_eval_embeddings()
        self.faithfulness = Faithfulness(llm=self.llm)
        self.answer_relevancy = AnswerRelevancy(
            llm=self.llm, embeddings=self.embeddings
        )
        self.context_precision = ContextPrecision(llm=self.llm)
        self.semantic_similarity = SemanticSimilarity(embeddings=self.embeddings)

    async def evaluate_sample(
        self,
        query: str,
        answer: str,
        contexts: List[str],
        reference: Optional[str] = None,
    ) -> EvaluationSampleRecord:
        metrics: dict[str, float] = {}

        faith_out = await self.faithfulness.ascore(
            user_input=query, response=answer, retrieved_contexts=contexts
        )
        metrics["faithfulness"] = float(faith_out.value)

        rel_out = await self.answer_relevancy.ascore(
            user_input=query, response=answer
        )
        metrics["answer_relevancy"] = float(rel_out.value)

        if reference:
            prec_out = await self.context_precision.ascore(
                user_input=query,
                reference=reference,
                retrieved_contexts=contexts,
            )
            metrics["context_precision"] = float(prec_out.value)

            sim_out = await self.semantic_similarity.ascore(
                reference=reference, response=answer
            )
            metrics["answer_similarity"] = float(sim_out.value)
        else:
            metrics["context_precision"] = 0.0
            metrics["answer_similarity"] = 0.0

        avg_score = sum(metrics.values()) / len(metrics)
        return EvaluationSampleRecord(
            query=query,
            answer=answer,
            contexts=contexts,
            scores=metrics,
            total_score=avg_score,
        )

    async def evaluate_async(
        self,
        queries: List[str],
        answers: List[str],
        contexts_list: List[List[str]],
        references: Optional[List[str]] = None,
    ) -> List[EvaluationSampleRecord]:
        tasks = []
        for i in range(len(queries)):
            ref = references[i] if references else None
            tasks.append(
                self.evaluate_sample(
                    query=queries[i],
                    answer=answers[i],
                    contexts=contexts_list[i],
                    reference=ref,
                )
            )
        return await asyncio.gather(*tasks)

    def evaluate(
        self,
        queries: List[str],
        answers: List[str],
        contexts_list: List[List[str]],
        references: Optional[List[str]] = None,
    ) -> List[EvaluationSampleRecord]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        coro = self.evaluate_async(queries, answers, contexts_list, references)

        if loop and loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        elif loop:
            return loop.run_until_complete(coro)
        return asyncio.run(coro)

    def evaluate_single(
        self,
        query: str,
        answer: str,
        contexts: List[str],
        reference: Optional[str] = None,
    ) -> EvaluationSampleRecord:
        return asyncio.run(
            self.evaluate_sample(query, answer, contexts, reference)
        )

    def evaluate_batch(
        self,
        queries: List[str],
        answers: List[str],
        contexts_list: List[List[str]],
        references: Optional[List[str]] = None,
    ) -> List[EvaluationSampleRecord]:
        return self.evaluate(
            queries=queries,
            answers=answers,
            contexts_list=contexts_list,
            references=references,
        )

    def get_aggregated_metrics(
        self, results: List[EvaluationSampleRecord]
    ) -> AggregatedMetrics:
        if not results:
            return AggregatedMetrics()

        count = len(results)
        return AggregatedMetrics(
            faithfulness=sum(r.scores["faithfulness"] for r in results) / count,
            answer_relevancy=sum(r.scores["answer_relevancy"] for r in results)
            / count,
            context_precision=sum(r.scores["context_precision"] for r in results)
            / count,
            answer_similarity=sum(r.scores["answer_similarity"] for r in results)
            / count,
            total_score=sum(r.total_score for r in results) / count,
        )

    def is_healthy(self) -> bool:
        return self.llm is not None and self.embeddings is not None


RAGASEvaluator = RagasBenchmarkRunner


def get_ragas_evaluator() -> RagasBenchmarkRunner:
    return RagasBenchmarkRunner()
