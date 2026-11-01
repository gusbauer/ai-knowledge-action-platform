import pytest

from langgraph.checkpoint.memory import (
    InMemorySaver,
)

from app.agents.agent_graph import (
    build_agent_graph,
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
        self.calls.append(question)

        return (
            "Fake RAG answer",
            [],
        )


@pytest.mark.asyncio
async def test_same_thread_keeps_messages():
    graph = build_agent_graph(
        rag_service=FakeRAGService(),
        checkpointer=InMemorySaver(),
    )

    config = {
        "configurable": {
            "thread_id": (
                "conversation-1"
            )
        }
    }

    first = await graph.ainvoke(
        {
            "question": (
                "¿Qué versión tiene "
                "el sistema?"
            )
        },
        config=config,
    )

    assert len(
        first["messages"]
    ) == 2

    second = await graph.ainvoke(
        {
            "question": (
                "¿Cuál es el estado "
                "del sistema?"
            )
        },
        config=config,
    )

    assert len(
        second["messages"]
    ) == 4


@pytest.mark.asyncio
async def test_different_threads_are_isolated():
    graph = build_agent_graph(
        rag_service=FakeRAGService(),
        checkpointer=InMemorySaver(),
    )

    first = await graph.ainvoke(
        {
            "question": (
                "¿Qué versión tiene "
                "el sistema?"
            )
        },
        config={
            "configurable": {
                "thread_id": "thread-a"
            }
        },
    )

    second = await graph.ainvoke(
        {
            "question": (
                "¿Qué versión tiene "
                "el sistema?"
            )
        },
        config={
            "configurable": {
                "thread_id": "thread-b"
            }
        },
    )

    assert len(
        first["messages"]
    ) == 2

    assert len(
        second["messages"]
    ) == 2