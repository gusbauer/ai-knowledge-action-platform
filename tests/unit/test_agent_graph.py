import pytest

from app.agents.agent_graph import (
    build_agent_graph,
)
from app.models.document_chunk import (
    DocumentChunk,
)


class FakeRAGService:
    def __init__(self):
        self.calls = []

    async def answer(
        self,
        question: str,
        limit: int,
        min_similarity: float,
    ):
        self.calls.append(
            {
                "question": question,
                "limit": limit,
                "min_similarity": (
                    min_similarity
                ),
            }
        )

        chunk = DocumentChunk(
            id=10,
            document_id=2,
            position=0,
            content=(
                "RAG retrieves relevant "
                "context before generation."
            ),
            character_count=47,
        )

        return (
            "RAG utiliza contexto recuperado.",
            [
                (
                    chunk,
                    0.20,
                )
            ],
        )


@pytest.mark.asyncio
async def test_knowledge_route_uses_rag():
    rag_service = FakeRAGService()

    graph = build_agent_graph(
        rag_service
    )

    result = await graph.ainvoke(
        {
            "question": (
                "¿Qué es RAG?"
            ),
            "limit": 3,
            "min_similarity": 0.40,
        }
    )

    assert (
        result["handled_by"]
        == "knowledge"
    )

    assert result["answer"] == (
        "RAG utiliza contexto recuperado."
    )

    assert len(
        result["sources"]
    ) == 1

    assert (
        result["sources"][0][
            "chunk_id"
        ]
        == 10
    )

    assert (
        result["sources"][0][
            "similarity"
        ]
        == pytest.approx(
            0.80
        )
    )

    assert rag_service.calls == [
        {
            "question": "¿Qué es RAG?",
            "limit": 3,
            "min_similarity": 0.40,
        }
    ]
    
@pytest.mark.asyncio
async def test_system_route_does_not_use_rag():
    rag_service = FakeRAGService()

    graph = build_agent_graph(
        rag_service
    )

    result = await graph.ainvoke(
        {
            "question": (
                "¿Qué versión tiene "
                "el sistema?"
            ),
        }
    )

    assert (
        result["handled_by"]
        == "system"
    )

    assert rag_service.calls == []