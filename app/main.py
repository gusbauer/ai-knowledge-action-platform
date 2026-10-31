from app.api.routes.documents import router as documents_router
from fastapi import FastAPI
from app.api.routes.rag import router as rag_router

from contextlib import asynccontextmanager

from app.core.error_handlers import (
    register_exception_handlers,
)
from app.core.redis import redis_client
from app.core.config import settings
from app.api.routes.system import router as system_router

from app.core.logging_config import (
    configure_logging,
)
from app.middleware.request_logging import (
    RequestLoggingMiddleware,
)

configure_logging()

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    yield

    await redis_client.aclose()
    
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan
)
register_exception_handlers(app)
app.add_middleware(
    RequestLoggingMiddleware
)

app.include_router(system_router)
app.include_router(documents_router)
app.include_router(rag_router)