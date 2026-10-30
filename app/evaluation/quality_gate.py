from dataclasses import dataclass

from app.evaluation.retrieval_metrics import (
    RetrievalMetrics,
)


@dataclass(frozen=True)
class QualityGateResult:
    passed: bool
    precision_regression: float
    recall_regression: float
    hit_rate_regression: float


def evaluate_quality_gate(
    baseline: RetrievalMetrics,
    candidate: RetrievalMetrics,
    max_regression: float,
) -> QualityGateResult:
    if max_regression < 0:
        raise ValueError(
            "max_regression cannot be negative."
        )

    precision_regression = (
        baseline.precision_at_k
        - candidate.precision_at_k
    )

    recall_regression = (
        baseline.recall_at_k
        - candidate.recall_at_k
    )

    hit_rate_regression = (
        baseline.hit_rate_at_k
        - candidate.hit_rate_at_k
    )

    passed = all(
        regression <= max_regression
        for regression in (
            precision_regression,
            recall_regression,
            hit_rate_regression,
        )
    )

    return QualityGateResult(
        passed=passed,
        precision_regression=precision_regression,
        recall_regression=recall_regression,
        hit_rate_regression=hit_rate_regression,
    )