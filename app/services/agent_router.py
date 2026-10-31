from typing import Protocol

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
)

from app.agents.state import (
    RouteName,
)
from app.services.ollama_provider import (
    LLMProviderError,
)


class RouteDecision(BaseModel):
    route: RouteName

    reason: str = Field(
        min_length=1,
        max_length=300,
    )


class StructuredRoutingProvider(
    Protocol
):
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict,
    ) -> str:
        ...


class AgentRoutingError(
    RuntimeError
):
    pass


ROUTER_SYSTEM_PROMPT = """
You classify requests for an AI
Knowledge & Action Platform.

Choose exactly one route:

system:
Questions about this platform itself,
including its version, health, status,
environment or runtime metadata.

knowledge:
Questions requiring information from
uploaded documents or the knowledge base.

Return the decision using the provided
JSON schema.
""".strip()


class LLMQuestionRouter:
    def __init__(
        self,
        provider: StructuredRoutingProvider,
    ):
        self.provider = provider

    async def classify(
        self,
        question: str,
    ) -> RouteDecision:
        try:
            raw = (
                await self.provider
                .generate_structured(
                    system_prompt=(
                        ROUTER_SYSTEM_PROMPT
                    ),
                    user_prompt=question,
                    schema=(
                        RouteDecision
                        .model_json_schema()
                    ),
                )
            )

            return (
                RouteDecision
                .model_validate_json(
                    raw
                )
            )

        except (
            ValidationError,
            LLMProviderError,
        ) as exc:
            raise AgentRoutingError(
                "LLM routing failed."
            ) from exc