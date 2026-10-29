from dataclasses import dataclass
def precision_at_k(
    retrieved_ids: list[int],
    relevant_ids: set[int],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )

    top_k = retrieved_ids[:k]

    if not top_k:
        return 0.0

    relevant_retrieved = sum(
        1
        for chunk_id in top_k
        if chunk_id in relevant_ids
    )

    return relevant_retrieved / len(top_k)


def recall_at_k(
    retrieved_ids: list[int],
    relevant_ids: set[int],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )

    if not relevant_ids:
        return 0.0

    top_k = retrieved_ids[:k]

    relevant_retrieved = sum(
        1
        for chunk_id in top_k
        if chunk_id in relevant_ids
    )

    return relevant_retrieved / len(relevant_ids)


def hit_rate_at_k(
    retrieved_ids: list[int],
    relevant_ids: set[int],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )

    top_k = retrieved_ids[:k]

    has_relevant_result = any(
        chunk_id in relevant_ids
        for chunk_id in top_k
    )

    return 1.0 if has_relevant_result else 0.0

@dataclass(frozen=True)
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float
    hit_rate_at_k: float


def evaluate_retrieval(
    retrieved_ids: list[int],
    relevant_ids: set[int],
    k: int,
) -> RetrievalMetrics:
    return RetrievalMetrics(
        precision_at_k=precision_at_k(
            retrieved_ids,
            relevant_ids,
            k,
        ),
        recall_at_k=recall_at_k(
            retrieved_ids,
            relevant_ids,
            k,
        ),
        hit_rate_at_k=hit_rate_at_k(
            retrieved_ids,
            relevant_ids,
            k,
        ),
    )