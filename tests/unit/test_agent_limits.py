import pytest

from langchain_core.messages import (
    AIMessage,
)
from langgraph.errors import (
    GraphRecursionError,
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


class InfiniteToolModel:
    def bind_tools(
        self,
        tools,
    ):
        return self

    async def ainvoke(
        self,
        messages,
    ):
        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": (
                        "get_system_info"
                    ),
                    "args": {},
                    "id": "loop-call",
                    "type": "tool_call",
                }
            ],
        )


@pytest.mark.asyncio
async def test_agent_recursion_limit():
    graph = build_tool_calling_graph(
        rag_service=FakeRAGService(),
        model=InfiniteToolModel(),
    )

    with pytest.raises(
        GraphRecursionError
    ):
        await graph.ainvoke(
            {
                "question": (
                    "Comprueba "
                    "el sistema"
                )
            },
            config={
                "recursion_limit": 4,
            },
        )