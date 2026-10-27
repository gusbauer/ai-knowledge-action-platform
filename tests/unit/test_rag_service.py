import pytest

from app.models.document_chunk import DocumentChunk
from app.services.rag_service import (
    INSUFFICIENT_CONTEXT_RESPONSE,
    RAGService,
)


class FakeLLM:
    def __init__(
        self,
        response: str,
    ) -> None:
        self.response = response
        self.calls = []

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
            }
        )

        return self.response


class FakeRetriever:
    def __init__(
        self,
        matches: list[
            tuple[DocumentChunk, float]
        ],
    ) -> None:
        self.matches = matches
        self.last_query_embedding = None
        self.last_limit = None

    async def semantic_search(
        self,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[
        tuple[DocumentChunk, float]
    ]:
        self.last_query_embedding = (
            query_embedding
        )
        self.last_limit = limit

        return self.matches[:limit]


async def fake_embedding_generator(
    texts: list[str],
) -> list[list[float]]:
    return [
        [0.1, 0.2, 0.3]
        for _ in texts
    ]


def create_chunk() -> DocumentChunk:
    content = (
        "RAG combines retrieval "
        "with language model generation."
    )

    return DocumentChunk(
        id=1,
        document_id=5,
        position=0,
        content=content,
        character_count=len(content),
    )
    
@pytest.mark.asyncio
async def test_rag_uses_relevant_context():
    chunk = create_chunk()

    retriever = FakeRetriever(
        matches=[
            (
                chunk,
                0.20,
            )
        ]
    )

    llm = FakeLLM(
        response=(
            "RAG combina recuperación "
            "y generación."
        )
    )

    service = RAGService(
        chunk_retriever=retriever,
        llm=llm,
        embedding_generator=(
            fake_embedding_generator
        ),
    )

    answer, matches = await service.answer(
        question="¿Qué es RAG?",
        limit=5,
        min_similarity=0.5,
    )

    assert answer == (
        "RAG combina recuperación "
        "y generación."
    )

    assert len(matches) == 1

    assert len(llm.calls) == 1

    assert (
        "RAG combines retrieval"
        in llm.calls[0]["user_prompt"]
    )

    assert (
        "¿Qué es RAG?"
        in llm.calls[0]["user_prompt"]
    )
    
@pytest.mark.asyncio
async def test_rag_does_not_call_llm_without_relevant_context():
    chunk = create_chunk()

    retriever = FakeRetriever(
        matches=[
            (
                chunk,
                0.80,
            )
        ]
    )

    llm = FakeLLM(
        response="This should not be used."
    )

    service = RAGService(
        chunk_retriever=retriever,
        llm=llm,
        embedding_generator=(
            fake_embedding_generator
        ),
    )

    answer, matches = await service.answer(
        question=(
            "¿Cómo cocinar una tortilla?"
        ),
        limit=5,
        min_similarity=0.5,
    )

    assert (
        answer
        == INSUFFICIENT_CONTEXT_RESPONSE
    )

    assert matches == []

    assert llm.calls == []
    
@pytest.mark.asyncio
async def test_rag_passes_limit_to_retriever():
    chunk = create_chunk()

    retriever = FakeRetriever(
        matches=[
            (
                chunk,
                0.10,
            )
        ]
    )

    llm = FakeLLM(
        response="Answer"
    )

    service = RAGService(
        chunk_retriever=retriever,
        llm=llm,
        embedding_generator=(
            fake_embedding_generator
        ),
    )

    await service.answer(
        question="¿Qué es RAG?",
        limit=3,
        min_similarity=0.5,
    )

    assert retriever.last_limit == 3

    assert (
        retriever.last_query_embedding
        == [0.1, 0.2, 0.3]
    )