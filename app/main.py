from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import (
    AsyncPostgresSaver,
)

from app.api.routes.agent import (
    router as agent_router,
)
from app.api.routes.documents import (
    router as documents_router,
)
from app.api.routes.rag import (
    router as rag_router,
)
from app.api.routes.system import (
    router as system_router,
)
from app.core.config import settings
from app.core.error_handlers import (
    register_exception_handlers,
)
from app.core.logging_config import (
    configure_logging,
)
from app.core.redis import redis_client
from app.middleware.request_logging import (
    RequestLoggingMiddleware,
)


configure_logging()


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    async with (
        AsyncPostgresSaver
        .from_conn_string(
            settings
            .checkpoint_database_url
        )
    ) as checkpointer:
        await checkpointer.setup()

        app.state.agent_checkpointer = (
            checkpointer
        )

        try:
            yield
        finally:
            await redis_client.aclose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
)


register_exception_handlers(app)


app.add_middleware(
    RequestLoggingMiddleware
)


app.include_router(
    system_router
)

app.include_router(
    documents_router
)

app.include_router(
    rag_router
)

app.include_router(
    agent_router
)