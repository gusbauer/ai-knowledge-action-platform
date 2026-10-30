import pytest

from app.evaluation.quality_gate import (
    evaluate_quality_gate,
)
from app.evaluation.retrieval_metrics import (
    RetrievalMetrics,
)


def test_quality_gate_passes_small_regression():
    baseline = RetrievalMetrics(
        precision_at_k=0.90,
        recall_at_k=0.80,
        hit_rate_at_k=1.00,
    )

    candidate = RetrievalMetrics(
        precision_at_k=0.88,
        recall_at_k=0.77,
        hit_rate_at_k=1.00,
    )

    result = evaluate_quality_gate(
        baseline=baseline,
        candidate=candidate,
        max_regression=0.05,
    )

    assert result.passed is True


def test_quality_gate_rejects_large_regression():
    baseline = RetrievalMetrics(
        precision_at_k=0.90,
        recall_at_k=0.80,
        hit_rate_at_k=1.00,
    )

    candidate = RetrievalMetrics(
        precision_at_k=0.70,
        recall_at_k=0.50,
        hit_rate_at_k=0.50,
    )

    result = evaluate_quality_gate(
        baseline=baseline,
        candidate=candidate,
        max_regression=0.05,
    )

    assert result.passed is False


def test_quality_gate_rejects_negative_tolerance():
    metrics = RetrievalMetrics(
        precision_at_k=1.0,
        recall_at_k=1.0,
        hit_rate_at_k=1.0,
    )

    with pytest.raises(ValueError):
        evaluate_quality_gate(
            baseline=metrics,
            candidate=metrics,
            max_regression=-0.1,
        )