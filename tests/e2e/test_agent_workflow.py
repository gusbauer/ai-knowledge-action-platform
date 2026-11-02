from fastapi.testclient import (
    TestClient,
)
from langchain_core.messages import (
    AIMessage,
)
from langgraph.checkpoint.memory import (
    InMemorySaver,
)

from app.agents.dependencies import (
    get_agent_graph,
)
from app.agents.tool_calling_graph import (
    build_tool_calling_graph,
)
from app.api.routes import (
    agent as agent_routes,
)
from app.main import app
from app.services.rate_limiter import (
    RateLimitDecision,
)


class FakeRAGService:
    async def retrieve(
        self,
        question: str,
        limit: int,
        min_similarity: float,
    ):
        return []


class FakeSystemModel:
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
                        "id": (
                            "system-call"
                        ),
                        "type": (
                            "tool_call"
                        ),
                    }
                ],
            )

        return AIMessage(
            content=(
                "La plataforma está "
                "funcionando correctamente."
            )
        )


async def allow_request(
    identifier: str,
):
    return RateLimitDecision(
        allowed=True,
        limit=10,
        remaining=9,
        retry_after=60,
    )


def test_agent_http_to_tool_workflow(
    monkeypatch,
):
    graph = build_tool_calling_graph(
        rag_service=FakeRAGService(),
        model=FakeSystemModel(),
        checkpointer=InMemorySaver(),
    )

    app.dependency_overrides[
        get_agent_graph
    ] = lambda: graph

    monkeypatch.setattr(
        agent_routes,
        "check_rag_rate_limit",
        allow_request,
    )

    client = TestClient(app)

    try:
        response = client.post(
            "/agent/ask",
            json={
                "question": (
                    "¿Qué versión tiene "
                    "esta plataforma?"
                ),
                "thread_id": (
                    "e2e-system-thread"
                ),
            },
        )

        assert (
            response.status_code
            == 200
        )

        body = response.json()

        assert (
            body["status"]
            == "completed"
        )

        assert (
            body["route"]
            == "system"
        )

        assert (
            body["tool_used"]
            == "get_system_info"
        )

        assert (
            body["thread_id"]
            == "e2e-system-thread"
        )

    finally:
        app.dependency_overrides.clear()