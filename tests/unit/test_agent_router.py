import pytest
from app.services.agent_router import (
    AgentRoutingError,
    LLMQuestionRouter,
)
from app.services.agent_router import (
    LLMQuestionRouter,
)
class InvalidProvider:
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict,
    ) -> str:
        return """
        {
          "route": "something_invalid"
        }
        """


@pytest.mark.asyncio
async def test_llm_router_rejects_invalid_output():
    router = LLMQuestionRouter(
        InvalidProvider()
    )

    with pytest.raises(
        AgentRoutingError
    ):
        await router.classify(
            "Test question"
        )

class FakeStructuredProvider:
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict,
    ) -> str:
        return """
        {
          "route": "system",
          "reason": "Runtime metadata question."
        }
        """


@pytest.mark.asyncio
async def test_llm_router_returns_structured_route():
    router = LLMQuestionRouter(
        FakeStructuredProvider()
    )

    decision = await router.classify(
        "¿En qué entorno está "
        "ejecutándose la plataforma?"
    )

    assert (
        decision.route
        == "system"
    )

    assert (
        decision.reason
        == "Runtime metadata question."
    )