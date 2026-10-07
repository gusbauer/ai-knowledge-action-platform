from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.system import router as system_router


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

app.include_router(system_router)