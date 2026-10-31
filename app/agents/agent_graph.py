from typing import Protocol

from app.agents.routing_graph import (
    build_routing_graph,
)
from app.agents.state import (
    AgentSourceState,
    AgentState,
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


def build_agent_graph(
    rag_service: RAGAnswerService,
):
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

    def system_handler(
        state: AgentState,
    ) -> dict:
        return {
            "answer": (
                "System route selected."
            ),
            "sources": [],
            "handled_by": "system",
        }

    return build_routing_graph(
        knowledge_handler=(
            knowledge_handler
        ),
        system_handler=(
            system_handler
        ),
    )