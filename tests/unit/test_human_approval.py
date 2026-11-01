import pytest

from langchain_core.messages import (
    AIMessage,
)
from langgraph.checkpoint.memory import (
    InMemorySaver,
)
from langgraph.types import (
    Command,
)

from app.agents.tool_calling_graph import (
    build_tool_calling_graph,
)


class FakeRAGService:
    async def retrieve(
        self,
        question: str,
        limit: int,
        min_similarity: float,
    ):
        return []


class FakeCacheModel:
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
                            "clear_embedding_cache"
                        ),
                        "args": {},
                        "id": "clear-1",
                        "type": "tool_call",
                    }
                ],
            )

        return AIMessage(
            content=(
                "La operación ha "
                "finalizado."
            )
        )


@pytest.mark.asyncio
async def test_cache_clear_requires_approval():
    graph = build_tool_calling_graph(
        rag_service=FakeRAGService(),
        model=FakeCacheModel(),
        checkpointer=InMemorySaver(),
    )

    config = {
        "configurable": {
            "thread_id": (
                "approval-test"
            )
        }
    }

    first = await graph.ainvoke(
        {
            "question": (
                "Borra la caché "
                "de embeddings"
            )
        },
        config=config,
    )

    assert "__interrupt__" in first

    resumed = await graph.ainvoke(
        Command(
            resume={
                "approved": False,
                "note": (
                    "No ejecutar"
                ),
            }
        ),
        config=config,
    )

    assert (
        resumed["tool_used"]
        == "clear_embedding_cache"
    )