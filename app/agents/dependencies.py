from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.agents.agent_graph import (
    build_agent_graph,
)
from app.db.dependencies import get_db
from app.repositories.document_chunk import (
    DocumentChunkRepository,
)
from app.services.ollama_provider import (
    OllamaProvider,
)
from app.services.rag_service import (
    RAGService,
)


def get_agent_graph(
    session: AsyncSession = Depends(
        get_db
    ),
):
    repository = DocumentChunkRepository(
        session
    )

    rag_service = RAGService(
        chunk_retriever=repository,
        llm=OllamaProvider(),
    )

    return build_agent_graph(
        rag_service
    )