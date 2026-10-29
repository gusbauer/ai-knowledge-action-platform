import pytest

from app.evaluation.retrieval_metrics import (
    evaluate_retrieval,
    hit_rate_at_k,
    precision_at_k,
    recall_at_k,
)


def test_precision_at_k():
    retrieved = [
        3,
        12,
        7,
    ]

    relevant = {
        3,
        7,
    }

    result = precision_at_k(
        retrieved,
        relevant,
        k=3,
    )

    assert result == pytest.approx(
        2 / 3
    )


def test_recall_at_k():
    retrieved = [
        3,
        12,
        7,
    ]

    relevant = {
        3,
        7,
        20,
        25,
    }

    result = recall_at_k(
        retrieved,
        relevant,
        k=3,
    )

    assert result == pytest.approx(
        0.5
    )


def test_hit_rate_returns_one_when_relevant_result_exists():
    result = hit_rate_at_k(
        retrieved_ids=[
            12,
            15,
            3,
        ],
        relevant_ids={
            3,
        },
        k=3,
    )

    assert result == 1.0


def test_hit_rate_returns_zero_when_no_relevant_result_exists():
    result = hit_rate_at_k(
        retrieved_ids=[
            12,
            15,
            18,
        ],
        relevant_ids={
            3,
        },
        k=3,
    )

    assert result == 0.0
    
def test_evaluate_retrieval_returns_all_metrics():
    metrics = evaluate_retrieval(
        retrieved_ids=[
            3,
            12,
            7,
        ],
        relevant_ids={
            3,
            7,
        },
        k=3,
    )

    assert (
        metrics.precision_at_k
        == pytest.approx(
            2 / 3
        )
    )

    assert (
        metrics.recall_at_k
        == pytest.approx(
            1.0
        )
    )

    assert (
        metrics.hit_rate_at_k
        == 1.0
    )
@pytest.mark.parametrize(
    "metric_function",
    [
        precision_at_k,
        recall_at_k,
        hit_rate_at_k,
    ],
)
def test_metrics_reject_invalid_k(
    metric_function,
):
    with pytest.raises(
        ValueError
    ):
        metric_function(
            retrieved_ids=[1, 2],
            relevant_ids={1},
            k=0,
        )