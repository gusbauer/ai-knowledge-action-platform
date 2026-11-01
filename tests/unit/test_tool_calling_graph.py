import pytest

from langchain_core.messages import (
    AIMessage,
)

from app.agents.tool_calling_graph import (
    build_tool_calling_graph,
)
from app.models.document_chunk import (
    DocumentChunk,
)


class FakeRAGService:
    async def retrieve(
        self,
        question: str,
        limit: int,
        min_similarity: float,
    ):
        chunk = DocumentChunk(
            id=20,
            document_id=3,
            position=0,
            content=(
                "Embeddings represent "
                "semantic meaning as vectors."
            ),
            character_count=48,
        )

        return [
            (
                chunk,
                0.15,
            )
        ]


class FakeSystemToolModel:
    def __init__(self):
        self.calls = 0

    def bind_tools(
        self,
        tools,
    ):
        return self

    async def ainvoke(
        self,
        messages,
    ):
        self.calls += 1

        if self.calls == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": (
                            "get_system_info"
                        ),
                        "args": {},
                        "id": "call-system-1",
                        "type": "tool_call",
                    }
                ],
            )

        return AIMessage(
            content=(
                "La plataforma está "
                "ejecutándose correctamente."
            )
        )


@pytest.mark.asyncio
async def test_agent_dynamically_calls_system_tool():
    graph = build_tool_calling_graph(
        rag_service=FakeRAGService(),
        model=FakeSystemToolModel(),
    )

    result = await graph.ainvoke(
        {
            "question": (
                "¿En qué entorno está "
                "la plataforma?"
            )
        }
    )

    assert (
        result["tool_used"]
        == "get_system_info"
    )

    assert (
        result["route"]
        == "system"
    )

    assert (
        result["handled_by"]
        == "system"
    )

    assert (
        "plataforma"
        in result["answer"].lower()
    )
    
class FakeKnowledgeToolModel:
    def __init__(self):
        self.calls = 0

    def bind_tools(
        self,
        tools,
    ):
        return self

    async def ainvoke(
        self,
        messages,
    ):
        self.calls += 1

        if self.calls == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": (
                            "search_knowledge"
                        ),
                        "args": {
                            "question": (
                                "¿Qué son "
                                "los embeddings?"
                            )
                        },
                        "id": (
                            "call-knowledge-1"
                        ),
                        "type": "tool_call",
                    }
                ],
            )

        return AIMessage(
            content=(
                "Los embeddings representan "
                "significado semántico "
                "mediante vectores."
            )
        )


@pytest.mark.asyncio
async def test_agent_dynamically_calls_knowledge_tool():
    graph = build_tool_calling_graph(
        rag_service=FakeRAGService(),
        model=FakeKnowledgeToolModel(),
    )

    result = await graph.ainvoke(
        {
            "question": (
                "¿Qué son los embeddings?"
            )
        }
    )

    assert (
        result["tool_used"]
        == "search_knowledge"
    )

    assert (
        result["route"]
        == "knowledge"
    )

    assert len(
        result["sources"]
    ) == 1

    assert (
        result["sources"][0][
            "chunk_id"
        ]
        == 20
    )