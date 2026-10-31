import logging
import time
from uuid import uuid4

from app.core.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS,
)
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.requests import Request


logger = logging.getLogger(
    "app.request"
)


class RequestLoggingMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        request_id = (
            request.headers.get(
                "X-Request-ID"
            )
            or uuid4().hex
        )

        request.state.request_id = (
            request_id
        )

        start_time = (
            time.perf_counter()
        )

        try:
            response = await call_next(
                request
            )

        except Exception:
            duration_ms = (
                time.perf_counter()
                - start_time
            ) * 1000

            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(
                        duration_ms,
                        2,
                    ),
                },
            )

            raise

        duration_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        response.headers[
            "X-Request-ID"
        ] = request_id
        route = request.scope.get(
            "route"
        )

        metric_path = getattr(
            route,
            "path",
            request.url.path,
        )

        HTTP_REQUESTS.labels(
            method=request.method,
            path=metric_path,
            status_code=str(
                response.status_code
            ),
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            path=metric_path,
        ).observe(
            duration_ms / 1000
        )
        
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": (
                    response.status_code
                ),
                "duration_ms": round(
                    duration_ms,
                    2,
                ),
            },
        )

        return response