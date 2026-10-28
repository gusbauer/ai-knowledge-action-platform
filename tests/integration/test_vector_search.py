import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk import (
    DocumentChunkRepository,
)


EMBEDDING_DIMENSION = 384


def create_vector(
    active_index: int,
) -> list[float]:
    vector = [
        0.0
        for _ in range(
            EMBEDDING_DIMENSION
        )
    ]

    vector[active_index] = 1.0

    return vector


@pytest.mark.integration
@pytest.mark.asyncio
async def test_semantic_search_returns_nearest_chunk(
    db_session: AsyncSession,
):
    document = Document(
        filename="integration-test.txt",
        content_type="text/plain",
        size_bytes=100,
    )

    db_session.add(document)

    await db_session.flush()

    rag_content = (
        "RAG combines information retrieval "
        "with language model generation."
    )

    unrelated_content = (
        "A database stores structured data."
    )

    rag_chunk = DocumentChunk(
        document_id=document.id,
        position=0,
        content=rag_content,
        character_count=len(rag_content),
        embedding=create_vector(0),
    )

    unrelated_chunk = DocumentChunk(
        document_id=document.id,
        position=1,
        content=unrelated_content,
        character_count=len(
            unrelated_content
        ),
        embedding=create_vector(1),
    )

    db_session.add_all(
        [
            rag_chunk,
            unrelated_chunk,
        ]
    )

    await db_session.commit()

    repository = DocumentChunkRepository(
        db_session
    )

    results = await repository.semantic_search(
        query_embedding=create_vector(0),
        limit=2,
    )

    assert len(results) == 2

    nearest_chunk, nearest_distance = (
        results[0]
    )

    assert nearest_chunk.content == rag_content

    assert nearest_distance == pytest.approx(
        0.0,
        abs=1e-6,
    )