import json
from pathlib import Path

import pytest
from sqlalchemy import delete
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
    generate_document_embeddings,
    generate_embeddings,
    generate_query_embeddings,
)


DATASET_PATH = (
    Path(__file__).parent
    / "data"
    / "retrieval_dataset.json"
)


async def prepare_chunks(
    db_session: AsyncSession,
    chunks_data: list[dict],
    embeddings: list[list[float]],
) -> dict[str, int]:
    await db_session.execute(
        delete(DocumentChunk)
    )

    await db_session.execute(
        delete(Document)
    )

    document = Document(
        filename="embedding-experiment.txt",
        content_type="text/plain",
    )

    db_session.add(document)

    await db_session.flush()

    chunks = []

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

    return key_to_id

def build_cases(
    dataset: dict,
    key_to_id: dict[str, int],
) -> list[RetrievalEvaluationCase]:
    return [
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
    
@pytest.mark.integration
@pytest.mark.asyncio
async def test_compare_embedding_strategies(
    db_session: AsyncSession,
):
    dataset = json.loads(
        DATASET_PATH.read_text(
            encoding="utf-8"
        )
    )

    chunks_data = dataset["chunks"]

    contents = [
        chunk["content"]
        for chunk in chunks_data
    ]

    repository = DocumentChunkRepository(
        db_session
    )

    baseline_embeddings = (
        await generate_embeddings(
            contents
        )
    )

    baseline_ids = await prepare_chunks(
        db_session,
        chunks_data,
        baseline_embeddings,
    )

    baseline_cases = build_cases(
        dataset,
        baseline_ids,
    )

    baseline_report = await evaluate_retriever(
        repository=repository,
        embedding_generator=generate_embeddings,
        cases=baseline_cases,
        k=2,
    )

    candidate_embeddings = (
        await generate_document_embeddings(
            contents
        )
    )

    candidate_ids = await prepare_chunks(
        db_session,
        chunks_data,
        candidate_embeddings,
    )

    candidate_cases = build_cases(
        dataset,
        candidate_ids,
    )

    candidate_report = await evaluate_retriever(
        repository=repository,
        embedding_generator=generate_query_embeddings,
        cases=candidate_cases,
        k=2,
    )

    print()
    print("=== EMBEDDING STRATEGY EXPERIMENT ===")

    print()
    print("BASELINE: encode()")
    print(
        "Precision@2: "
        f"{baseline_report.mean_precision_at_k:.4f}"
    )
    print(
        "Recall@2: "
        f"{baseline_report.mean_recall_at_k:.4f}"
    )
    print(
        "Hit Rate@2: "
        f"{baseline_report.mean_hit_rate_at_k:.4f}"
    )

    print()
    print(
        "CANDIDATE: "
        "encode_document() / encode_query()"
    )
    print(
        "Precision@2: "
        f"{candidate_report.mean_precision_at_k:.4f}"
    )
    print(
        "Recall@2: "
        f"{candidate_report.mean_recall_at_k:.4f}"
    )
    print(
        "Hit Rate@2: "
        f"{candidate_report.mean_hit_rate_at_k:.4f}"
    )

    assert baseline_report.case_count == 4
    assert candidate_report.case_count == 4