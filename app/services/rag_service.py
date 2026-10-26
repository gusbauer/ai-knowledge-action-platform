from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_chunk import (
    DocumentChunkRepository,
)
from app.services.embedding_service import (
    generate_embeddings,
)
from app.services.ollama_provider import (
    LLMProviderError,
    OllamaProvider,
)


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


class RAGService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.chunk_repository = (
            DocumentChunkRepository(session)
        )

        self.llm = OllamaProvider()

    async def answer(
        self,
        question: str,
        limit: int,
        min_similarity: float,
    ) -> tuple[str, list]:
        query_embedding = (
            await generate_embeddings(
                [question]
            )
        )[0]

        matches = (
            await self.chunk_repository.semantic_search(
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
                "No tengo información suficiente "
                "en los documentos disponibles "
                "para responder a esa pregunta.",
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

        context = "\n\n".join(context_parts)

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