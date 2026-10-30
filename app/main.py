from app.api.routes.documents import router as documents_router
from fastapi import FastAPI
from app.api.routes.rag import router as rag_router

from app.core.config import settings
from app.api.routes.system import router as system_router

from app.core.logging_config import (
    configure_logging,
)
from app.middleware.request_logging import (
    RequestLoggingMiddleware,
)

configure_logging()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

app.add_middleware(
    RequestLoggingMiddleware
)

app.include_router(system_router)
app.include_router(documents_router)
app.include_router(rag_router)