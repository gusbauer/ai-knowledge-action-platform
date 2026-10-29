from collections.abc import Awaitable, Callable
from typing import Protocol
from app.services.embedding_service import (
    generate_query_embeddings,
)
from ..models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_query_embeddings
from app.services.llm_provider import LLMProvider


SYSTEM_PROMPT = """
You are a knowledge assistant.

Answer the user's question using only the provided context.

Rules:
- Do not invent information.
- If the context is insufficient, say that you do not have enough information.
- Do not use external knowledge to fill missing information.
- Answer clearly and concisely.
- Answer in the same language as the user's question.
""".strip()


INSUFFICIENT_CONTEXT_RESPONSE = (
    "No tengo información suficiente "
    "en los documentos disponibles "
    "para responder a esa pregunta."
)


EmbeddingGenerator = Callable[
    [list[str]],
    Awaitable[list[list[float]]],
]


class ChunkRetriever(Protocol):
    async def semantic_search(
        self,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        ...


class RAGService:
    def __init__(
        self,
        chunk_retriever: ChunkRetriever,
        llm: LLMProvider,
        embedding_generator: EmbeddingGenerator = generate_query_embeddings,
    ) -> None:
        self.chunk_retriever = chunk_retriever
        self.llm = llm
        self.embedding_generator = embedding_generator

    async def answer(
        self,
        question: str,
        limit: int,
        min_similarity: float,
    ) -> tuple[
        str,
        list[tuple[DocumentChunk, float]],
    ]:
        query_embedding = (
            await self.embedding_generator(
                [question]
            )
        )[0]

        matches = (
            await self.chunk_retriever.semantic_search(
                query_embedding=query_embedding,
                limit=limit,
            )
        )

        relevant_matches = [
            (chunk, distance)
            for chunk, distance in matches
            if (1.0 - distance) >= min_similarity
        ]

        if not relevant_matches:
            return (
                INSUFFICIENT_CONTEXT_RESPONSE,
                [],
            )

        context_parts = []

        for chunk, distance in relevant_matches:
            similarity = 1.0 - distance

            context_parts.append(
                (
                    f"[Document {chunk.document_id} "
                    f"- Chunk {chunk.position} "
                    f"- Similarity {similarity:.4f}]\n"
                    f"{chunk.content}"
                )
            )

        context = "\n\n".join(
            context_parts
        )

        user_prompt = f"""
CONTEXT:

{context}

QUESTION:

{question}
""".strip()

        answer = await self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return answer, relevant_matches