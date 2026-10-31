from fastapi import Depends
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.db.dependencies import get_db

from fastapi import APIRouter

from app.core.config import settings

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.core.redis import redis_client

from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)
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

@router.get(
    "/metrics",
    include_in_schema=False,
)
def metrics():
    return Response(
        content=generate_latest(),
        headers={
            "Content-Type": (
                CONTENT_TYPE_LATEST
            )
        },
    )
    
@router.get(
    "/health/live"
)
async def liveness():
    return {
        "status": "alive",
    }
    
@router.get(
    "/health/ready"
)
async def readiness(
    session: AsyncSession = Depends(
        get_db
    ),
):
    try:
        await session.execute(
            text("SELECT 1")
        )

    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "database": "unavailable",
                "cache": "unknown",
            },
        )

    cache_status = "connected"

    try:
        await redis_client.ping()

    except RedisError:
        cache_status = "degraded"

    return {
        "status": "ready",
        "database": "connected",
        "cache": cache_status,
    }