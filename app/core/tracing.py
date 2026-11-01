import os

from app.core.config import settings


def configure_ai_tracing() -> None:
    os.environ[
        "LANGSMITH_TRACING"
    ] = (
        "true"
        if settings.langsmith_tracing
        else "false"
    )

    os.environ[
        "LANGSMITH_PROJECT"
    ] = settings.langsmith_project

    if settings.langsmith_api_key:
        os.environ[
            "LANGSMITH_API_KEY"
        ] = settings.langsmith_api_key