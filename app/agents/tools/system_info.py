from langchain_core.tools import (
    tool,
)

from app.core.config import settings


@tool
def get_system_info() -> dict[str, str]:
    """
    Return safe metadata about the
    AI Knowledge & Action Platform.
    """

    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": (
            settings.environment
        ),
    }