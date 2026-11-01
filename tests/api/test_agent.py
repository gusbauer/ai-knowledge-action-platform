from fastapi.testclient import TestClient

from app.agents.dependencies import (
    get_agent_graph,
)
from app.api.routes import agent as agent_routes
from app.main import app
from app.services.rate_limiter import (
    RateLimitDecision,
)


client = TestClient(app)


class FakeAgentGraph:
    async def ainvoke(
        self,
        state: dict,
        config=None,
    ):
        return {
            "question": (
                state["question"]
            ),
            "route": "system",
            "handled_by": "system",
            "answer": (
                "AI Knowledge & Action "
                "Platform v0.1.0"
            ),
            "sources": [],
            "tool_used": (
                "get_system_info"
            ),
        }


async def allow_rate_limit(
    identifier: str,
):
    return RateLimitDecision(
        allowed=True,
        limit=10,
        remaining=9,
        retry_after=60,
    )


def test_agent_ask(
    monkeypatch,
):
    app.dependency_overrides[
        get_agent_graph
    ] = lambda: FakeAgentGraph()

    monkeypatch.setattr(
        agent_routes,
        "check_rag_rate_limit",
        allow_rate_limit,
    )

    try:
        response = client.post(
            "/agent/ask",
            json={
                "question": (
                    "¿Qué versión tiene "
                    "el sistema?"
                ),
                "thread_id": (
                    "test-thread-1"
                ),
            },
        )

        assert (
            response.status_code
            == 200
        )

        body = response.json()

        assert (
            body["thread_id"]
            == "test-thread-1"
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
            body["sources"]
            == []
        )

    finally:
        app.dependency_overrides.clear()