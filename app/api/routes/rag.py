from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)

from app.services.rate_limiter import (
    check_rag_rate_limit,
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
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
):

    client_identifier = (
        request.client.host
        if request.client
        else "unknown"
    )

    decision = await check_rag_rate_limit(
        client_identifier
    )

    rate_limit_headers = {
        "X-RateLimit-Limit": str(
            decision.limit
        ),
        "X-RateLimit-Remaining": str(
            decision.remaining
        ),
        "X-RateLimit-Reset": str(
            decision.retry_after
        ),
    }

    if not decision.allowed:
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "RAG request rate limit exceeded."
            ),
            headers={
                **rate_limit_headers,
                "Retry-After": str(
                    decision.retry_after
                ),
            },
        )

    for header, value in (
        rate_limit_headers.items()
    ):
        response.headers[
            header
        ] = value
    # Rate limiting
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