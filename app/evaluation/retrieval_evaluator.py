from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.evaluation.retrieval_metrics import (
    RetrievalMetrics,
    evaluate_retrieval,
)
from app.repositories.document_chunk import (
    DocumentChunkRepository,
)


EmbeddingGenerator = Callable[
    [list[str]],
    Awaitable[list[list[float]]],
]


@dataclass(frozen=True)
class RetrievalEvaluationCase:
    query: str
    relevant_ids: set[int]


@dataclass(frozen=True)
class RetrievalCaseResult:
    query: str
    retrieved_ids: list[int]
    metrics: RetrievalMetrics


@dataclass(frozen=True)
class RetrievalEvaluationReport:
    k: int
    case_count: int
    mean_precision_at_k: float
    mean_recall_at_k: float
    mean_hit_rate_at_k: float
    cases: list[RetrievalCaseResult]


async def evaluate_retriever(
    repository: DocumentChunkRepository,
    embedding_generator: EmbeddingGenerator,
    cases: list[RetrievalEvaluationCase],
    k: int,
) -> RetrievalEvaluationReport:
    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )

    if not cases:
        raise ValueError(
            "At least one evaluation case is required."
        )

    results: list[RetrievalCaseResult] = []

    for case in cases:
        query_embedding = (
            await embedding_generator(
                [case.query]
            )
        )[0]

        matches = await repository.semantic_search(
            query_embedding=query_embedding,
            limit=k,
        )

        retrieved_ids = [
            chunk.id
            for chunk, _ in matches
        ]

        metrics = evaluate_retrieval(
            retrieved_ids=retrieved_ids,
            relevant_ids=case.relevant_ids,
            k=k,
        )

        results.append(
            RetrievalCaseResult(
                query=case.query,
                retrieved_ids=retrieved_ids,
                metrics=metrics,
            )
        )

    case_count = len(results)

    mean_precision = sum(
        result.metrics.precision_at_k
        for result in results
    ) / case_count

    mean_recall = sum(
        result.metrics.recall_at_k
        for result in results
    ) / case_count

    mean_hit_rate = sum(
        result.metrics.hit_rate_at_k
        for result in results
    ) / case_count

    return RetrievalEvaluationReport(
        k=k,
        case_count=case_count,
        mean_precision_at_k=mean_precision,
        mean_recall_at_k=mean_recall,
        mean_hit_rate_at_k=mean_hit_rate,
        cases=results,
    )