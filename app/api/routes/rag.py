from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.document_chunk import (
    DocumentChunkRepository,
)
from app.services.ollama_provider import (
    LLMProviderError,
    OllamaProvider,
)

from app.db.dependencies import get_db
from app.schemas.rag import (
    RAGRequest,
    RAGResponse,
    RAGSource,
)
from app.services.embedding_service import (
    EmbeddingGenerationError,
)
from app.services.ollama_provider import (
    LLMProviderError,
)
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@router.post(
    "/ask",
    response_model=RAGResponse,
)
async def ask_rag(
    payload: RAGRequest,
    session: AsyncSession = Depends(get_db),
):
    chunk_repository = DocumentChunkRepository(session)
    service = RAGService(
        chunk_retriever=chunk_repository,
        llm=OllamaProvider(),
    )


    try:
        answer, matches = await service.answer(
            question=payload.question,
            limit=payload.limit,
            min_similarity=payload.min_similarity,
        )

    except (
        EmbeddingGenerationError,
        LLMProviderError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    sources = [
        RAGSource(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            position=chunk.position,
            similarity=round(
                1.0 - distance,
                4,
            ),
            content=chunk.content,
        )
        for chunk, distance in matches
    ]

    return RAGResponse(
        question=payload.question,
        answer=answer,
        sources=sources,
    )