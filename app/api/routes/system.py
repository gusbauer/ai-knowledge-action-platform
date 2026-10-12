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