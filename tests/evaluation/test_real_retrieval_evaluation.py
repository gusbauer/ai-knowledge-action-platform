import json
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.evaluation.retrieval_evaluator import (
    RetrievalEvaluationCase,
    evaluate_retriever,
)
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk import (
    DocumentChunkRepository,
)
from app.services.embedding_service import (
    generate_embeddings,
)


DATASET_PATH = (
    Path(__file__).parent
    / "data"
    / "retrieval_dataset.json"
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_retrieval_evaluation(
    db_session: AsyncSession,
):
    dataset = json.loads(
        DATASET_PATH.read_text(
            encoding="utf-8"
        )
    )

    chunks_data = dataset["chunks"]

    document = Document(
        filename="retrieval-evaluation.txt",
        content_type="text/plain",
    )

    db_session.add(document)

    await db_session.flush()

    contents = [
        chunk["content"]
        for chunk in chunks_data
    ]

    embeddings = await generate_embeddings(
        contents
    )

    chunks: list[DocumentChunk] = []

    for position, (
        chunk_data,
        embedding,
    ) in enumerate(
        zip(
            chunks_data,
            embeddings,
            strict=True,
        )
    ):
        content = chunk_data["content"]

        chunk = DocumentChunk(
            document_id=document.id,
            position=position,
            content=content,
            character_count=len(content),
            embedding=embedding,
        )

        chunks.append(chunk)

    db_session.add_all(chunks)

    await db_session.flush()

    key_to_id = {
        chunk_data["key"]: chunk.id
        for chunk_data, chunk in zip(
            chunks_data,
            chunks,
            strict=True,
        )
    }

    await db_session.commit()

    evaluation_cases = [
        RetrievalEvaluationCase(
            query=case["query"],
            relevant_ids={
                key_to_id[key]
                for key in case[
                    "relevant_keys"
                ]
            },
        )
        for case in dataset["cases"]
    ]

    repository = DocumentChunkRepository(
        db_session
    )

    report = await evaluate_retriever(
        repository=repository,
        embedding_generator=generate_embeddings,
        cases=evaluation_cases,
        k=2,
    )

    print()
    print("=== RETRIEVAL EVALUATION ===")
    print(
        f"Cases: {report.case_count}"
    )
    print(
        "Mean Precision@2: "
        f"{report.mean_precision_at_k:.4f}"
    )
    print(
        "Mean Recall@2: "
        f"{report.mean_recall_at_k:.4f}"
    )
    print(
        "Mean Hit Rate@2: "
        f"{report.mean_hit_rate_at_k:.4f}"
    )

    for result in report.cases:
        print()
        print(
            f"Query: {result.query}"
        )
        print(
            "Retrieved IDs: "
            f"{result.retrieved_ids}"
        )
        print(
            "Precision: "
            f"{result.metrics.precision_at_k:.4f}"
        )
        print(
            "Recall: "
            f"{result.metrics.recall_at_k:.4f}"
        )
        print(
            "Hit Rate: "
            f"{result.metrics.hit_rate_at_k:.4f}"
        )

    assert report.case_count == 4

    assert (
        0.0
        <= report.mean_precision_at_k
        <= 1.0
    )

    assert (
        0.0
        <= report.mean_recall_at_k
        <= 1.0
    )

    assert (
        0.0
        <= report.mean_hit_rate_at_k
        <= 1.0
    )