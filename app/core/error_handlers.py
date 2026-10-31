import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.errors import (
    ApplicationError,
)


logger = logging.getLogger(
    "app.errors"
)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    @app.exception_handler(
        ApplicationError
    )
    async def application_error_handler(
        request: Request,
        exc: ApplicationError,
    ):
        request_id = getattr(
            request.state,
            "request_id",
            None,
        )

        logger.warning(
            "application_error",
            extra={
                "request_id": request_id,
                "path": request.url.path,
            },
        )

        error = {
            "code": exc.code,
            "message": str(exc),
        }

        if request_id:
            error["request_id"] = (
                request_id
            )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": error,
            },
        )