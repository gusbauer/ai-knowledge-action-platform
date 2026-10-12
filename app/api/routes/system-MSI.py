from sqlalchemy import text

from app.db.session import engine
from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(tags=["System"])


@router.get("/")
def root():
    return {
        "message": f"{settings.app_name} API",
        "environment": settings.environment,
    }


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
    }
@router.get("/health/database")
async def database_health_check():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
        "check": result.scalar_one(),
    }