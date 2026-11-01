from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from langchain_ollama import (
    ChatOllama,
)

from app.agents.tool_calling_graph import (
    build_tool_calling_graph,
)
from app.core.config import settings
from langgraph.checkpoint.memory import (
    InMemorySaver,
)
from app.services.agent_router import (
    LLMQuestionRouter,
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

    agent_checkpointer = (
        InMemorySaver()
    )

    if (
        settings.agent_mode
        == "tool_calling"        
    ):
        model = ChatOllama(
            model=settings.ollama_model,
            base_url=(
                settings.ollama_base_url
            ),
            temperature=0,
        )

        return build_tool_calling_graph(
            rag_service=rag_service,
            model=model,
            checkpointer=(
                agent_checkpointer
            ),
        )
        
    router = LLMQuestionRouter(
        provider=OllamaProvider()
    )

    return build_agent_graph(
        rag_service=rag_service,
        router=router,
        checkpointer=(
            agent_checkpointer
        ),
    )