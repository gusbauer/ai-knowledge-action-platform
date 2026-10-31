from typing import Protocol

from app.agents.routing_graph import (
    build_routing_graph,
    classify_question,
)
from app.agents.state import (
    AgentSourceState,
    AgentState,
)
from app.agents.tools.system_info import (
    get_system_info,
)
from app.models.document_chunk import (
    DocumentChunk,
)


class RAGAnswerService(Protocol):
    async def answer(
        self,
        question: str,
        limit: int,
        min_similarity: float,
    ) -> tuple[
        str,
        list[
            tuple[
                DocumentChunk,
                float,
            ]
        ],
    ]:
        ...


class QuestionRouter(Protocol):
    async def classify(
        self,
        question: str,
    ):
        ...


def build_agent_graph(
    rag_service: RAGAnswerService,
    router: QuestionRouter | None = None,
):
    async def classifier_handler(
        state: AgentState,
    ) -> dict:
        if router is None:
            fallback = classify_question(
                state
            )

            return {
                **fallback,
                "routing_strategy": (
                    "deterministic"
                ),
                "routing_reason": (
                    "No LLM router configured."
                ),
            }

        try:
            decision = await router.classify(
                state[
                    "normalized_question"
                ]
            )

            return {
                "route": decision.route,
                "routing_strategy": "llm",
                "routing_reason": (
                    decision.reason
                ),
            }

        except Exception:
            fallback = classify_question(
                state
            )

            return {
                **fallback,
                "routing_strategy": (
                    "deterministic_fallback"
                ),
                "routing_reason": (
                    "LLM router unavailable."
                ),
            }

    async def knowledge_handler(
        state: AgentState,
    ) -> dict:
        question = state[
            "normalized_question"
        ]

        answer, matches = (
            await rag_service.answer(
                question=question,
                limit=state.get(
                    "limit",
                    5,
                ),
                min_similarity=state.get(
                    "min_similarity",
                    0.25,
                ),
            )
        )

        sources: list[
            AgentSourceState
        ] = []

        for chunk, distance in matches:
            sources.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": (
                        chunk.document_id
                    ),
                    "position": (
                        chunk.position
                    ),
                    "similarity": (
                        1.0
                        - float(distance)
                    ),
                    "content": (
                        chunk.content
                    ),
                }
            )

        return {
            "answer": answer,
            "sources": sources,
            "handled_by": "knowledge",
        }

    async def system_handler(
        state: AgentState,
    ) -> dict:
        system_info = (
            await get_system_info.ainvoke(
                {}
            )
        )

        answer = (
            f"{system_info['app_name']} "
            f"v{system_info['version']} "
            f"está ejecutándose en el "
            f"entorno "
            f"{system_info['environment']}."
        )

        return {
            "answer": answer,
            "sources": [],
            "handled_by": "system",
            "tool_used": (
                "get_system_info"
            ),
        }

    return build_routing_graph(
        knowledge_handler=(
            knowledge_handler
        ),
        system_handler=(
            system_handler
        ),
        classifier_handler=(
            classifier_handler
        ),
    )