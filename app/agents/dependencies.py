from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.agent_graph import build_agent_graph
from app.agents.tool_calling_graph import build_tool_calling_graph
from app.core.config import settings
from app.db.dependencies import get_db
from app.repositories.document_chunk import DocumentChunkRepository
from app.services.agent_router import LLMQuestionRouter
from app.services.ollama_provider import OllamaProvider
from app.services.rag_service import RAGService


def get_agent_graph(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    checkpointer = request.app.state.agent_checkpointer
    repository = DocumentChunkRepository(session)

    rag_service = RAGService(
        chunk_retriever=repository,
        llm=OllamaProvider(),
    )

    if settings.agent_mode == "tool_calling":
        model = OllamaProvider()
        return build_tool_calling_graph(
            rag_service=rag_service,
            model=model,
            checkpointer=checkpointer,
        )

    router = LLMQuestionRouter(
        provider=OllamaProvider()
    )

    return build_agent_graph(
        rag_service=rag_service,
        router=router,
        checkpointer=checkpointer,
    )