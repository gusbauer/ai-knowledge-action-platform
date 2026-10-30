from fastapi import APIRouter

from app.core.config import settings

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.core.redis import redis_client

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
    
@router.get(
    "/health/cache"
)
async def cache_health_check():
    try:
        result = await redis_client.ping()

    except RedisError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail="Redis is unavailable.",
        ) from exc

    return {
        "status": "ok",
        "cache": "connected",
        "check": bool(result),
    }